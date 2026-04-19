import os
import resend 


RESEND_API_KEY = os.getenv("RESEND_API_KEY")

if not RESEND_API_KEY:
    print("⚠️ RESEND_API_KEY not set. Email sending disabled.")
else:
    resend.api_key = RESEND_API_KEY



FROM_EMAIL = os.getenv("FROM_EMAIL", "MedSchedule AI <onboarding@resend.dev>")


def send_daily_appointments_email(clinic_email, doctor_name, appointments):
    if not appointments:
        return

    rows = ""
    for a in appointments:
        rows += f"""
        <tr>
            <td>{a.patient.name}</td>
            <td>{a.patient.phone}</td>
            <td>{a.appointment_time}</td>
        </tr>
        """

    html = f"""
        <div style="font-family: Arial, Helvetica, sans-serif; background-color: #f6f8fb; padding: 24px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">

            <!-- Header -->
            <div style="background-color: #2563eb; color: #ffffff; padding: 16px 20px;">
            <h2 style="margin: 0; font-size: 20px;">
                🩺 MedSchedule AI
            </h2>
            <p style="margin: 4px 0 0; font-size: 14px; opacity: 0.9;">
                Daily Appointment Summary
            </p>
            </div>

            <!-- Body -->
            <div style="padding: 20px;">
            <p style="font-size: 15px; color: #333333; margin-bottom: 16px;">
                Hello <strong>Dr. {doctor_name}</strong>,
            </p>

            <p style="font-size: 14px; color: #555555; margin-bottom: 20px;">
                Here is your appointment schedule for today:
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse: collapse; font-size: 14px;">
                <thead>
                <tr style="background-color: #f1f5f9;">
                    <th style="padding: 10px; border: 1px solid #e5e7eb; text-align: left;">
                    Patient Name
                    </th>
                    <th style="padding: 10px; border: 1px solid #e5e7eb; text-align: left;">
                    Phone
                    </th>
                    <th style="padding: 10px; border: 1px solid #e5e7eb; text-align: left;">
                    Time
                    </th>
                </tr>
                </thead>
                <tbody>
                {rows}
                </tbody>
            </table>

            <p style="font-size: 13px; color: #6b7280; margin-top: 20px;">
                You can manage or update appointments from your dashboard.
            </p>
            </div>

            <!-- Footer -->
            <div style="background-color: #f9fafb; padding: 12px 20px; text-align: center; font-size: 12px; color: #9ca3af;">
            © {doctor_name}'s Clinic · Powered by MedSchedule AI
            </div>

        </div>
        </div>
        """


    resend.Emails.send({
        "from": FROM_EMAIL,

        "to": ["medschedule.ai@gmail.com"],
        "subject": f"Today's Appointments – {doctor_name}",
        "html": html,
    })
