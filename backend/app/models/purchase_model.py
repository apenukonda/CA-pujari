"""
Purchase Model for Firestore Database
Handles course/webinar purchases, payments, and access control
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from app.constants.statuses import PurchaseStatus, PaymentStatus


class PaymentDetails(BaseModel):
    """Payment transaction details"""
    gateway: str  # stripe, razorpay, paypal, etc.
    gateway_transaction_id: str
    gateway_payment_id: Optional[str] = None
    currency: str = "USD"
    amount_paid: float
    fee_amount: float = 0.0
    net_amount: float
    payment_method: Optional[str] = None
    card_last_four: Optional[str] = None
    card_type: Optional[str] = None
    gateway_fee_percentage: float = 0.0
    tax_amount: float = 0.0
    tax_percentage: float = 0.0
    discount_applied: float = 0.0
    coupon_code: Optional[str] = None
    coupon_discount_percentage: float = 0.0


class PurchaseItem(BaseModel):
    """Individual item in a purchase"""
    item_id: str  # course_id or webinar_id
    item_type: str  # "course" or "webinar"
    title: str
    description: Optional[str] = None
    price: float
    quantity: int = 1
    subtotal: float
    discount_amount: float = 0.0
    final_price: float
    thumbnail_url: Optional[str] = None


class RefundDetails(BaseModel):
    """Refund transaction details"""
    refund_id: Optional[str] = None
    gateway_refund_id: Optional[str] = None
    amount_refunded: float
    refund_reason: str
    refund_date: datetime
    refund_status: str  # pending, completed, failed
    gateway_fee_refunded: float = 0.0
    processed_by: Optional[str] = None  # Admin UID who processed refund
    admin_notes: Optional[str] = None


class AccessDetails(BaseModel):
    """User access information for purchased content"""
    access_granted: bool = False
    access_granted_at: Optional[datetime] = None
    access_expires_at: Optional[datetime] = None
    access_renewed_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_duration_days: Optional[int] = None  # 365 for lifetime access
    access_source: str = "purchase"  # purchase, gift, trial, etc.
    access_notes: Optional[str] = None


class BillingDetails(BaseModel):
    """Billing address and customer information"""
    customer_name: str
    customer_email: str
    customer_phone: Optional[str] = None
    billing_address: Optional[Dict[str, Any]] = None
    tax_id: Optional[str] = None
    company_name: Optional[str] = None
    vat_number: Optional[str] = None


class PurchaseAnalytics(BaseModel):
    """Purchase analytics and metrics"""
    source: str = "direct"  # direct, referral, social, etc.
    referrer: Optional[str] = None
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None
    discount_code_used: Optional[str] = None
    time_of_day: Optional[str] = None
    day_of_week: Optional[str] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    country: Optional[str] = None


class PurchaseModel:
    """Purchase model for Firestore operations"""
    
    COLLECTION_NAME = "purchases"
    
    def __init__(self):
        from app.core.firebase import db
        self.db = db
        self.collection = self.db.collection(self.COLLECTION_NAME)
    
    def create_purchase_data(
        self,
        user_uid: str,
        user_email: str,
        user_name: str,
        items: List[PurchaseItem],
        total_amount: float,
        payment_details: PaymentDetails,
        billing_details: BillingDetails,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create purchase data structure
        
        Args:
            user_uid: User Firebase UID
            user_email: User email
            user_name: User name
            items: List of purchased items
            total_amount: Total purchase amount
            payment_details: Payment transaction details
            billing_details: Billing information
            additional_data: Additional purchase data
            
        Returns:
            Dictionary with purchase data
        """
        # Calculate subtotal and discounts
        subtotal = sum(item.subtotal for item in items)
        total_discount = sum(item.discount_amount for item in items)
        
        # Verify totals match
        expected_final_amount = sum(item.final_price for item in items)
        if abs(expected_final_amount - total_amount) > 0.01:
            raise ValueError("Total amount mismatch with item prices")
        
        # Create purchase items data
        purchase_items = [item.dict() for item in items]
        
        purchase_data = {
            "id": "",  # Will be set when created
            "purchase_number": self._generate_purchase_number(),
            "user": {
                "uid": user_uid,
                "email": user_email,
                "name": user_name
            },
            "items": purchase_items,
            "pricing": {
                "subtotal": subtotal,
                "total_discount": total_discount,
                "total_amount": total_amount,
                "currency": payment_details.currency,
                "tax_amount": payment_details.tax_amount,
                "tax_percentage": payment_details.tax_percentage,
                "gateway_fee": payment_details.fee_amount,
                "net_amount": payment_details.net_amount,
                "coupon_code": payment_details.coupon_code,
                "coupon_discount": payment_details.discount_applied
            },
            "payment": {
                "status": PaymentStatus.PENDING.value,
                "details": payment_details.dict(),
                "gateway_response": {},
                "failure_reason": None,
                "retries_count": 0,
                "last_retry_at": None
            },
            "billing": billing_details.dict(),
            "status": PurchaseStatus.PENDING.value,
            "refund": None,
            "access": {
                "granted": False,
                "items": []
            },
            "analytics": PurchaseAnalytics().dict(),
            "timeline": {
                "created_at": datetime.utcnow(),
                "payment_completed_at": None,
                "access_granted_at": None,
                "refunded_at": None,
                "updated_at": datetime.utcnow()
            },
            "metadata": {}
        }
        
        # Set access details for each item
        access_items = []
        for item in items:
            # Determine access duration based on item type
            access_duration_days = None  # Lifetime access for courses
            if item.item_type == "webinar":
                # Webinar access typically expires after 30 days
                access_duration_days = 30
            
            access_item = AccessDetails(
                access_granted=False,
                access_duration_days=access_duration_days
            ).dict()
            
            access_item["item_id"] = item.item_id
            access_item["item_type"] = item.item_type
            access_item["title"] = item.title
            access_items.append(access_item)
        
        purchase_data["access"]["items"] = access_items
        
        if additional_data:
            purchase_data["metadata"].update(additional_data)
        
        return purchase_data
    
    def _generate_purchase_number(self) -> str:
        """Generate unique purchase number"""
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        import random
        random_suffix = random.randint(1000, 9999)
        
        return f"ORD-{timestamp}-{random_suffix}"
    
    async def create_purchase(
        self,
        user_uid: str,
        user_email: str,
        user_name: str,
        items: List[PurchaseItem],
        total_amount: float,
        payment_details: PaymentDetails,
        billing_details: BillingDetails,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new purchase
        
        Args:
            user_uid: User Firebase UID
            user_email: User email
            user_name: User name
            items: List of purchased items
            total_amount: Total purchase amount
            payment_details: Payment transaction details
            billing_details: Billing information
            additional_data: Additional purchase data
            
        Returns:
            Purchase ID
        """
        purchase_data = self.create_purchase_data(
            user_uid, user_email, user_name, items, total_amount,
            payment_details, billing_details, additional_data
        )
        
        # Create purchase document
        doc_ref = self.collection.document()
        purchase_data["id"] = doc_ref.id
        
        await doc_ref.set(purchase_data)
        
        return doc_ref.id
    
    async def get_purchase(self, purchase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get purchase by ID
        
        Args:
            purchase_id: Purchase ID
            
        Returns:
            Purchase data or None if not found
        """
        doc = self.collection.document(purchase_id).get()
        
        if doc.exists:
            purchase_data = doc.to_dict()
            purchase_data["id"] = doc.id
            return purchase_data
        
        return None
    
    async def get_user_purchases(
        self,
        user_uid: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get user's purchase history
        
        Args:
            user_uid: User Firebase UID
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of user purchases
        """
        query = self.collection \
            .where("user.uid", "==", user_uid) \
            .order_by("timeline.created_at", direction="DESCENDING")
        
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        purchases = []
        for doc in docs:
            purchase_data = doc.to_dict()
            purchase_data["id"] = doc.id
            purchases.append(purchase_data)
        
        return purchases
    
    async def get_purchases_by_item(
        self,
        item_id: str,
        item_type: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get purchases for a specific item (course/webinar)
        
        Args:
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            limit: Results limit
            offset: Results offset
            
        Returns:
            List of purchases for the item
        """
        # This is a more complex query that requires array field filtering
        # For now, we'll get all purchases and filter in memory
        # In production, consider denormalizing this data for better performance
        
        query = self.collection \
            .where("status", "==", PurchaseStatus.COMPLETED.value) \
            .order_by("timeline.created_at", direction="DESCENDING")
        
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        purchases = []
        for doc in docs:
            purchase_data = doc.to_dict()
            purchase_data["id"] = doc.id
            
            # Filter by item
            items = purchase_data.get("items", [])
            has_item = any(
                item.get("item_id") == item_id and item.get("item_type") == item_type
                for item in items
            )
            
            if has_item:
                purchases.append(purchase_data)
        
        return purchases
    
    async def update_payment_status(
        self,
        purchase_id: str,
        status: PaymentStatus,
        gateway_response: Optional[Dict[str, Any]] = None,
        failure_reason: Optional[str] = None
    ) -> bool:
        """
        Update payment status
        
        Args:
            purchase_id: Purchase ID
            status: New payment status
            gateway_response: Gateway response data
            failure_reason: Failure reason if payment failed
            
        Returns:
            True if successful
        """
        doc_ref = self.collection.document(purchase_id)
        
        updates = {
            "payment.status": status.value,
            "timeline.updated_at": datetime.utcnow()
        }
        
        if gateway_response:
            updates["payment.gateway_response"] = gateway_response
        
        if failure_reason:
            updates["payment.failure_reason"] = failure_reason
        
        if status == PaymentStatus.COMPLETED:
            updates["timeline.payment_completed_at"] = datetime.utcnow()
        
        await doc_ref.update(updates)
        
        return True
    
    async def complete_purchase(self, purchase_id: str) -> bool:
        """
        Complete a purchase and grant access
        
        Args:
            purchase_id: Purchase ID
            
        Returns:
            True if successful
        """
        doc_ref = self.collection.document(purchase_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        purchase_data = doc.to_dict()
        
        # Update purchase status
        updates = {
            "status": PurchaseStatus.COMPLETED.value,
            "payment.status": PaymentStatus.COMPLETED.value,
            "timeline.payment_completed_at": datetime.utcnow(),
            "timeline.updated_at": datetime.utcnow()
        }
        
        # Grant access for all items
        access_items = purchase_data.get("access", {}).get("items", [])
        
        for access_item in access_items:
            # Set access granted details
            access_item["access_granted"] = True
            access_item["access_granted_at"] = datetime.utcnow()
            
            # Set expiration if applicable
            if access_item.get("access_duration_days"):
                access_item["access_expires_at"] = datetime.utcnow() + timedelta(
                    days=access_item["access_duration_days"]
                )
        
        updates["access.items"] = access_items
        updates["access.granted"] = True
        updates["timeline.access_granted_at"] = datetime.utcnow()
        
        await doc_ref.update(updates)
        
        return True
    
    async def process_refund(
        self,
        purchase_id: str,
        refund_amount: float,
        refund_reason: str,
        processed_by: Optional[str] = None,
        admin_notes: Optional[str] = None
    ) -> bool:
        """
        Process refund for a purchase
        
        Args:
            purchase_id: Purchase ID
            refund_amount: Amount to refund
            refund_reason: Reason for refund
            processed_by: Admin UID who processed refund
            admin_notes: Additional admin notes
            
        Returns:
            True if successful
        """
        doc_ref = self.collection.document(purchase_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        purchase_data = doc.to_dict()
        
        # Create refund details
        refund_details = RefundDetails(
            amount_refunded=refund_amount,
            refund_reason=refund_reason,
            refund_date=datetime.utcnow(),
            refund_status="completed",
            processed_by=processed_by,
            admin_notes=admin_notes
        ).dict()
        
        # Revoke access for all items
        access_items = purchase_data.get("access", {}).get("items", [])
        for access_item in access_items:
            access_item["access_granted"] = False
            access_item["access_notes"] = "Access revoked due to refund"
        
        # Update purchase data
        updates = {
            "status": PurchaseStatus.REFUNDED.value,
            "refund": refund_details,
            "access.items": access_items,
            "access.granted": False,
            "timeline.refunded_at": datetime.utcnow(),
            "timeline.updated_at": datetime.utcnow()
        }
        
        await doc_ref.update(updates)
        
        return True
    
    async def has_access_to_item(
        self,
        user_uid: str,
        item_id: str,
        item_type: str
    ) -> bool:
        """
        Check if user has access to a specific item
        
        Args:
            user_uid: User Firebase UID
            item_id: Course or webinar ID
            item_type: "course" or "webinar"
            
        Returns:
            True if user has access
        """
        query = self.collection \
            .where("user.uid", "==", user_uid) \
            .where("status", "==", PurchaseStatus.COMPLETED.value) \
            .where("access.granted", "==", True)
        
        docs = query.get()
        
        now = datetime.utcnow()
        
        for doc in docs:
            purchase_data = doc.to_dict()
            access_items = purchase_data.get("access", {}).get("items", [])
            
            for access_item in access_items:
                if (access_item.get("item_id") == item_id and 
                    access_item.get("item_type") == item_type and
                    access_item.get("access_granted", False)):
                    
                    # Check if access has expired
                    expires_at = access_item.get("access_expires_at")
                    if expires_at and expires_at <= now:
                        return False
                    
                    return True
        
        return False
    
    async def get_user_accessible_items(
        self,
        user_uid: str,
        item_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all items user has access to
        
        Args:
            user_uid: User Firebase UID
            item_type: Filter by item type ("course" or "webinar")
            
        Returns:
            List of accessible items
        """
        query = self.collection \
            .where("user.uid", "==", user_uid) \
            .where("status", "==", PurchaseStatus.COMPLETED.value) \
            .where("access.granted", "==", True)
        
        docs = query.get()
        
        accessible_items = []
        now = datetime.utcnow()
        
        for doc in docs:
            purchase_data = doc.to_dict()
            access_items = purchase_data.get("access", {}).get("items", [])
            
            for access_item in access_items:
                if (access_item.get("access_granted", False) and
                    (item_type is None or access_item.get("item_type") == item_type)):
                    
                    # Check if access has expired
                    expires_at = access_item.get("access_expires_at")
                    if expires_at and expires_at <= now:
                        continue
                    
                    # Add purchase context
                    item_with_context = access_item.copy()
                    item_with_context["purchase_id"] = doc.id
                    item_with_context["purchase_number"] = purchase_data.get("purchase_number")
                    item_with_context["purchased_at"] = purchase_data.get("timeline", {}).get("payment_completed_at")
                    
                    accessible_items.append(item_with_context)
        
        return accessible_items
    
    async def search_purchases(
        self,
        search_term: str = "",
        user_uid: str = "",
        status: Optional[PurchaseStatus] = None,
        payment_status: Optional[PaymentStatus] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
        sort_by: str = "timeline.created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search purchases with filters
        
        Args:
            search_term: Search term for customer name/email/purchase number
            user_uid: Filter by user
            status: Filter by purchase status
            payment_status: Filter by payment status
            start_date: Filter by start date
            end_date: Filter by end date
            min_amount: Minimum purchase amount
            max_amount: Maximum purchase amount
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            limit: Results limit
            offset: Results offset
            
        Returns:
            Dictionary with purchases and pagination info
        """
        query = self.collection
        
        # Apply filters
        if status:
            query = query.where("status", "==", status.value)
        
        if payment_status:
            query = query.where("payment.status", "==", payment_status.value)
        
        if user_uid:
            query = query.where("user.uid", "==", user_uid)
        
        # Apply date range filter
        if start_date:
            query = query.where("timeline.created_at", ">=", start_date)
        if end_date:
            query = query.where("timeline.created_at", "<=", end_date)
        
        # Apply sorting
        direction = "DESCENDING" if sort_order.lower() == "desc" else "ASCENDING"
        
        if sort_by in ["pricing.total_amount", "pricing.subtotal"]:
            query = query.order_by(sort_by, direction=direction)
        else:
            query = query.order_by(sort_by, direction=direction)
        
        # Apply pagination
        if offset > 0:
            docs = query.offset(offset).limit(limit).get()
        else:
            docs = query.limit(limit).get()
        
        purchases = []
        for doc in docs:
            purchase_data = doc.to_dict()
            purchase_data["id"] = doc.id
            
            # Apply additional filters
            skip = False
            
            # Search term filter
            if search_term and not skip:
                search_fields = [
                    purchase_data.get("purchase_number", ""),
                    purchase_data.get("user", {}).get("name", ""),
                    purchase_data.get("user", {}).get("email", ""),
                    " ".join([item.get("title", "") for item in purchase_data.get("items", [])])
                ]
                
                if not any(search_term.lower() in field.lower() for field in search_fields if field):
                    skip = True
            
            # Amount filter
            if not skip and (min_amount is not None or max_amount is not None):
                total_amount = purchase_data.get("pricing", {}).get("total_amount", 0)
                
                if min_amount is not None and total_amount < min_amount:
                    skip = True
                elif max_amount is not None and total_amount > max_amount:
                    skip = True
            
            if not skip:
                purchases.append(purchase_data)
        
        # Get total count for pagination
        count_query = self.collection
        
        if status:
            count_query = count_query.where("status", "==", status.value)
        if payment_status:
            count_query = count_query.where("payment.status", "==", payment_status.value)
        if user_uid:
            count_query = count_query.where("user.uid", "==", user_uid)
        
        total_count = len(count_query.get())
        
        return {
            "purchases": purchases,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count,
            "limit": limit,
            "offset": offset
        }
    
    async def get_purchase_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get purchase statistics
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with purchase statistics
        """
        query = self.collection
        
        # Apply date filters
        if start_date:
            query = query.where("timeline.created_at", ">=", start_date)
        if end_date:
            query = query.where("timeline.created_at", "<=", end_date)
        
        docs = query.get()
        
        stats = {
            "total_purchases": 0,
            "total_revenue": 0.0,
            "total_refunded_amount": 0.0,
            "unique_customers": 0,
            "purchases_by_status": {},
            "purchases_by_payment_status": {},
            "average_order_value": 0.0,
            "total_purchased_items": 0,
            "item_popularity": {},  # item_id -> purchase_count
            "monthly_revenue": {},  # month -> revenue
            "customer_purchase_frequency": {}  # uid -> purchase_count
        }
        
        customer_purchases = {}
        monthly_revenue = {}
        
        for doc in docs:
            purchase_data = doc.to_dict()
            stats["total_purchases"] += 1
            
            # Count by status
            status = purchase_data.get("status", "unknown")
            stats["purchases_by_status"][status] = stats["purchases_by_status"].get(status, 0) + 1
            
            # Count by payment status
            payment_status = purchase_data.get("payment", {}).get("status", "unknown")
            stats["purchases_by_payment_status"][payment_status] = stats["purchases_by_payment_status"].get(payment_status, 0) + 1
            
            # Revenue calculations
            total_amount = purchase_data.get("pricing", {}).get("total_amount", 0)
            stats["total_revenue"] += total_amount
            
            # Monthly revenue
            created_at = purchase_data.get("timeline", {}).get("created_at")
            if created_at:
                month_key = created_at.strftime("%Y-%m")
                monthly_revenue[month_key] = monthly_revenue.get(month_key, 0) + total_amount
            
            # Refunded amount
            if status == PurchaseStatus.REFUNDED.value:
                refund_amount = purchase_data.get("refund", {}).get("amount_refunded", 0)
                stats["total_refunded_amount"] += refund_amount
            
            # Customer tracking
            user_uid = purchase_data.get("user", {}).get("uid")
            if user_uid:
                customer_purchases[user_uid] = customer_purchases.get(user_uid, 0) + 1
            
            # Item popularity
            items = purchase_data.get("items", [])
            stats["total_purchased_items"] += len(items)
            
            for item in items:
                item_id = item.get("item_id")
                if item_id:
                    stats["item_popularity"][item_id] = stats["item_popularity"].get(item_id, 0) + 1
        
        # Calculate final metrics
        stats["unique_customers"] = len(customer_purchases)
        stats["average_order_value"] = stats["total_revenue"] / stats["total_purchases"] if stats["total_purchases"] > 0 else 0
        stats["monthly_revenue"] = monthly_revenue
        stats["customer_purchase_frequency"] = customer_purchases
        
        return stats
    
    async def get_customer_lifetime_value(self, user_uid: str) -> Dict[str, Any]:
        """
        Get customer lifetime value metrics
        
        Args:
            user_uid: User Firebase UID
            
        Returns:
            Dictionary with CLV metrics
        """
        query = self.collection \
            .where("user.uid", "==", user_uid) \
            .where("status", "==", PurchaseStatus.COMPLETED.value)
        
        docs = query.get()
        
        metrics = {
            "total_purchases": 0,
            "total_spent": 0.0,
            "average_order_value": 0.0,
            "first_purchase_date": None,
            "last_purchase_date": None,
            "purchased_items": [],
            "refund_count": 0,
            "refunded_amount": 0.0
        }
        
        purchased_items = []
        first_purchase_date = None
        last_purchase_date = None
        
        for doc in docs:
            purchase_data = doc.to_dict()
            metrics["total_purchases"] += 1
            
            # Calculate spending
            total_amount = purchase_data.get("pricing", {}).get("total_amount", 0)
            metrics["total_spent"] += total_amount
            
            # Track dates
            created_at = purchase_data.get("timeline", {}).get("created_at")
            if created_at:
                if not first_purchase_date or created_at < first_purchase_date:
                    first_purchase_date = created_at
                if not last_purchase_date or created_at > last_purchase_date:
                    last_purchase_date = created_at
            
            # Track purchased items
            items = purchase_data.get("items", [])
            for item in items:
                item_info = item.copy()
                item_info["purchase_date"] = created_at
                item_info["purchase_id"] = doc.id
                purchased_items.append(item_info)
            
            # Track refunds
            if purchase_data.get("status") == PurchaseStatus.REFUNDED.value:
                metrics["refund_count"] += 1
                refund_amount = purchase_data.get("refund", {}).get("amount_refunded", 0)
                metrics["refunded_amount"] += refund_amount
        
        # Calculate final metrics
        metrics["average_order_value"] = metrics["total_spent"] / metrics["total_purchases"] if metrics["total_purchases"] > 0 else 0
        metrics["first_purchase_date"] = first_purchase_date
        metrics["last_purchase_date"] = last_purchase_date
        metrics["purchased_items"] = purchased_items
        
        return metrics


# Helper functions for purchase operations
def create_payment_details(
    gateway: str,
    gateway_transaction_id: str,
    amount_paid: float,
    currency: str = "USD"
) -> PaymentDetails:
    """
    Create payment details
    
    Args:
        gateway: Payment gateway name
        gateway_transaction_id: Gateway transaction ID
        amount_paid: Amount paid by user
        currency: Currency code
        
    Returns:
        PaymentDetails object
    """
    return PaymentDetails(
        gateway=gateway,
        gateway_transaction_id=gateway_transaction_id,
        amount_paid=amount_paid,
        currency=currency,
        net_amount=amount_paid  # Will be updated with actual calculations
    )


def create_billing_details(
    customer_name: str,
    customer_email: str,
    customer_phone: Optional[str] = None,
    billing_address: Optional[Dict[str, Any]] = None
) -> BillingDetails:
    """
    Create billing details
    
    Args:
        customer_name: Customer full name
        customer_email: Customer email
        customer_phone: Customer phone number
        billing_address: Billing address dictionary
        
    Returns:
        BillingDetails object
    """
    return BillingDetails(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        billing_address=billing_address
    )


def create_purchase_item(
    item_id: str,
    item_type: str,
    title: str,
    price: float,
    quantity: int = 1,
    discount_amount: float = 0.0,
    description: Optional[str] = None,
    thumbnail_url: Optional[str] = None
) -> PurchaseItem:
    """
    Create purchase item
    
    Args:
        item_id: Course or webinar ID
        item_type: "course" or "webinar"
        title: Item title
        price: Item price
        quantity: Quantity purchased
        discount_amount: Discount amount
        description: Item description
        thumbnail_url: Item thumbnail URL
        
    Returns:
        PurchaseItem object
    """
    subtotal = price * quantity
    final_price = max(0, subtotal - discount_amount)
    
    return PurchaseItem(
        item_id=item_id,
        item_type=item_type,
        title=title,
        description=description,
        price=price,
        quantity=quantity,
        subtotal=subtotal,
        discount_amount=discount_amount,
        final_price=final_price,
        thumbnail_url=thumbnail_url
    )