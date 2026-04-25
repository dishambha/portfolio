from django.db import models


class ContactMessage(models.Model):
    MESSAGE_TYPES = [
        ("opportunity", "Job Opportunity"),
        ("project", "Project Collaboration"),
        ("query", "General Query"),
        ("review", "Review / Feedback"),
        ("other", "Other"),
    ]
    name = models.CharField(max_length=120)
    email = models.EmailField()
    msg_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default="query")
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notified_wa = models.BooleanField(default=False)  # WhatsApp sent?
    notified_em = models.BooleanField(default=False)  # Email sent?

    class Meta:
        ordering = ["-created_at"]
        app_label = "portfolio"

    def __str__(self):
        return f"[{self.msg_type}] {self.name} – {self.subject[:40]}"
