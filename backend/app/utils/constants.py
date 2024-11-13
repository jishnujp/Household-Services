class ServiceRequestStatus:
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

    @classmethod
    def all(cls):
        return [cls.PENDING, cls.ACCEPTED, cls.REJECTED, cls.COMPLETED, cls.CANCELLED]


class AllowableRoles:
    ADMIN = "admin"
    CUSTOMER = "customer"
    PROFESSIONAL = "professional"

    @classmethod
    def all(cls):
        return [cls.ADMIN, cls.CUSTOMER, cls.PROFESSIONAL]
