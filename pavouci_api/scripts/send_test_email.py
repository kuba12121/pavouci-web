import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pavouci_api.utils.email_utils import send_verification_email
from pavouci_api.settings import FROM_EMAIL

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('to', help='Recipient email')
    p.add_argument('--subject', default='Test email from Pavouci API')
    p.add_argument('--body', default='This is a test email from Pavouci API.')
    args = p.parse_args()

    if not FROM_EMAIL:
        print('FROM_EMAIL not configured in .env; set FROM_EMAIL and SMTP_* to send real emails.')
        print('You can still test by ensuring DEBUG_VERIFY_IN_RESPONSE=true and reading verification_link from /auth/register response.')
        sys.exit(1)

    ok = send_verification_email(args.to, args.subject, args.body)
    if ok:
        print('Email send OK')
    else:
        print('Email not sent; check SMTP settings and logs')
