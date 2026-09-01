from django.db import models


class User(models.Model):
    user_id = models.BigAutoField(primary_key=True, db_column="UserID")
    full_name = models.CharField(max_length=100, db_column="FullName")
    email = models.EmailField(max_length=255, unique=True, db_column="Email")
    phone = models.CharField(max_length=15, unique=True, db_column="Phone")
    password = models.CharField(max_length=255, db_column="Password")

    ROLE_CHOICES = [
        ("Customer", "Customer"),
        ("Owner", "Owner"),
        ("Admin", "Admin"),
    ]

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        db_column="Role"
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
        db_column="DateCreated"
    )

    class Meta:
        db_table = "USERS"

    def __str__(self):
        return self.full_name




class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True)

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        db_column='UserID'
    )

    vehicle_number = models.CharField(
        max_length=20,
        unique=True
    )

    vehicle_model = models.CharField(
        max_length=100
    )

    vehicle_type = models.CharField(
        max_length=30,
        choices=[
            ('Car', 'Car'),
            ('Bike', 'Bike'),
            ('Bus', 'Bus'),
            ('Other', 'Other'),
        ]
    )

    battery_capacity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'VEHICLES'

    def __str__(self):
        return self.vehicle_number



class Station(models.Model):
    station_id = models.BigAutoField(
        primary_key=True,
        db_column="StationID"
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="OwnerID",
        related_name="owned_stations"
    )

    station_name = models.CharField(
        max_length=100,
        db_column="StationName"
    )

    address = models.CharField(
        max_length=255,
        db_column="Address"
    )

    city = models.CharField(
        max_length=50,
        db_column="City"
    )

    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        db_column="Latitude"
    )

    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        db_column="Longitude"
    )

    opening_time = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column="OpeningTime"
    )

    closing_time = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        db_column="ClosingTime"
    )

    class Meta:
        db_table = "STATIONS"

    def __str__(self):
        return self.station_name


class Charger(models.Model):
    charger_id = models.BigAutoField(
        primary_key=True,
        db_column="ChargerID"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        db_column="StationID",
        related_name="chargers"
    )

    charger_number = models.IntegerField(
        db_column="ChargerNumber"
    )

    CHARGER_TYPE_CHOICES = [
        ("AC", "AC"),
        ("DC", "DC"),
    ]

    charger_type = models.CharField(
        max_length=30,
        choices=CHARGER_TYPE_CHOICES,
        db_column="ChargerType"
    )

    power_output = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_column="PowerOutput"
    )

    price_per_kwh = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_column="PricePerKWh"
    )

    CHARGER_STATUS_CHOICES = [
        ("Available", "Available"),
        ("Occupied", "Occupied"),
        ("Maintenance", "Maintenance"),
    ]

    status = models.CharField(
        max_length=20,
        choices=CHARGER_STATUS_CHOICES,
        db_column="Status"
    )

    class Meta:
        db_table = "CHARGERS"

        constraints = [
            models.UniqueConstraint(
                fields=["station", "charger_number"],
                name="UQ_CHARGERS_NUMBER"
            ),
            models.CheckConstraint(
                condition=models.Q(charger_type__in=["AC", "DC"]),
                name="CK_CHARGERS_TYPE"
            ),
            models.CheckConstraint(
                condition=models.Q(power_output__gt=0),
                name="CK_CHARGERS_POWER"
            ),
            models.CheckConstraint(
                condition=models.Q(price_per_kwh__gt=0),
                name="CK_CHARGERS_PRICE"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["Available", "Occupied", "Maintenance"]
                ),
                name="CK_CHARGERS_STATUS"
            ),
        ]

    def __str__(self):
        return f"{self.station.station_name} - Charger {self.charger_number}"



class Booking(models.Model):
    booking_id = models.BigAutoField(
        primary_key=True,
        db_column="BookingID"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="UserID",
        related_name="bookings"
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        db_column="VehicleID",
        related_name="bookings"
    )

    charger = models.ForeignKey(
        Charger,
        on_delete=models.CASCADE,
        db_column="ChargerID",
        related_name="bookings"
    )

    booking_date = models.DateTimeField(
        db_column="BookingDate"
    )

    start_time = models.DateTimeField(
        db_column="StartTime"
    )

    end_time = models.DateTimeField(
        db_column="EndTime"
    )

    BOOKING_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS_CHOICES,
        db_column="Status"
    )

    class Meta:
        db_table = "BOOKINGS"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="CK_BOOKINGS_TIME"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    status__in=[
                        "Pending",
                        "Confirmed",
                        "Completed",
                        "Cancelled"
                    ]
                ),
                name="CK_BOOKINGS_STATUS"
            ),
        ]

    def __str__(self):
        return f"Booking {self.booking_id}"




class ChargingSession(models.Model):
    session_id = models.BigAutoField(
        primary_key=True,
        db_column="SessionID"
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        db_column="BookingID",
        related_name="charging_sessions"
    )

    start_time = models.DateTimeField(
        db_column="StartTime"
    )

    end_time = models.DateTimeField(
        db_column="EndTime"
    )

    units_consumed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="UnitsConsumed"
    )

    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="TotalCost"
    )

    class Meta:
        db_table = "CHARGING_SESSIONS"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="CK_CHARGING_SESSIONS_TIME"
            ),
            models.CheckConstraint(
                condition=models.Q(units_consumed__gt=0),
                name="CK_CHARGING_SESSIONS_UNITS"
            ),
            models.CheckConstraint(
                condition=models.Q(total_cost__gte=0),
                name="CK_CHARGING_SESSIONS_COST"
            ),
        ]

    def __str__(self):
        return f"Session {self.session_id}"





class Payment(models.Model):
    payment_id = models.BigAutoField(
        primary_key=True,
        db_column="PaymentID"
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        db_column="BookingID",
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column="Amount"
    )

    PAYMENT_METHOD_CHOICES = [
        ("UPI", "UPI"),
        ("Card", "Card"),
        ("Cash", "Cash"),
    ]

    payment_method = models.CharField(
        max_length=30,
        choices=PAYMENT_METHOD_CHOICES,
        db_column="PaymentMethod"
    )

    PAYMENT_STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
        ("Refunded", "Refunded"),
    ]

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        db_column="PaymentStatus"
    )

    payment_date = models.DateTimeField(
        db_column="PaymentDate"
    )

    class Meta:
        db_table = "PAYMENTS"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="CK_PAYMENTS_AMOUNT"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    payment_method__in=["UPI", "Card", "Cash"]
                ),
                name="CK_PAYMENTS_METHOD"
            ),
            models.CheckConstraint(
                condition=models.Q(
                    payment_status__in=[
                        "Pending",
                        "Completed",
                        "Failed",
                        "Refunded"
                    ]
                ),
                name="CK_PAYMENTS_STATUS"
            ),
        ]

    def __str__(self):
        return f"Payment {self.payment_id}"



class MaintenanceReport(models.Model):
    report_id = models.BigAutoField(
        primary_key=True,
        db_column="ReportID"
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        db_column="BookingID",
        related_name="maintenance_reports"
    )

    charger = models.ForeignKey(
        Charger,
        on_delete=models.CASCADE,
        db_column="ChargerID",
        related_name="maintenance_reports"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="UserID",
        related_name="maintenance_reports"
    )

    issue_type = models.CharField(
        max_length=100,
        db_column="IssueType"
    )

    description = models.CharField(
        max_length=500,
        db_column="Description"
    )

    status = models.CharField(
        max_length=30,
        db_column="Status"
    )

    report_date = models.DateTimeField(
        db_column="ReportDate"
    )

    class Meta:
        db_table = "MAINTENANCE_REPORTS"

    def __str__(self):
        return f"Report {self.report_id}"






class MaintenanceVerification(models.Model):
    verification_id = models.BigAutoField(
        primary_key=True,
        db_column="VerificationID"
    )

    report = models.ForeignKey(
        MaintenanceReport,
        on_delete=models.CASCADE,
        db_column="ReportID",
        related_name="verifications"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="UserID",
        related_name="maintenance_verifications"
    )

    VERIFICATION_RESULT_CHOICES = [
        ("Approved", "Approved"),
        ("Rejected", "Rejected"),
        ("Pending", "Pending"),
    ]

    result = models.CharField(
        max_length=50,
        choices=VERIFICATION_RESULT_CHOICES,
        db_column="Result"
    )

    comments = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column="Comments"
    )

    verification_date = models.DateTimeField(
        db_column="VerificationDate"
    )

    class Meta:
        db_table = "MAINTENANCE_VERIFICATION"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    result__in=["Approved", "Rejected", "Pending"]
                ),
                name="CK_MAINT_VERIFICATION_RESULT"
            ),
        ]

    def __str__(self):
        return f"Verification {self.verification_id}"






class Notification(models.Model):
    notification_id = models.BigAutoField(
        primary_key=True,
        db_column="NotificationID"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="UserID",
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200,
        db_column="Title"
    )

    message = models.CharField(
        max_length=500,
        db_column="Message"
    )

    is_read = models.CharField(
        max_length=1,
        default="N",
        db_column="IsRead"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column="CreatedAt"
    )

    class Meta:
        db_table = "NOTIFICATIONS"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(is_read__in=["Y", "N"]),
                name="CK_NOTIFICATIONS_ISREAD"
            ),
        ]

    def __str__(self):
        return self.title









class Review(models.Model):
    review_id = models.BigAutoField(
        primary_key=True,
        db_column="ReviewID"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="UserID",
        related_name="reviews"
    )

    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE,
        db_column="StationID",
        related_name="reviews"
    )

    rating = models.IntegerField(
        db_column="Rating"
    )

    comments = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column="Comments"
    )

    review_date = models.DateTimeField(
        db_column="ReviewDate"
    )

    class Meta:
        db_table = "REVIEWS"

        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="CK_REVIEWS_RATING"
            ),
        ]

    def __str__(self):
        return f"Review {self.review_id}"




