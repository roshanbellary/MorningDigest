from flask import Blueprint, request, jsonify
from datetime import datetime
from app.services.email_processor import process_emails
from app.services.digest_generator import generate_digest
from app.services.gmail_service import GmailService

bp = Blueprint('api', __name__)
gmail_service = GmailService()

@bp.route('/process-emails', methods=['POST'])
def process_emails_endpoint():
    try:
        # Get date and industries from request
        data = request.json
        date_str = data.get('date')
        target_industries = data.get('industries', [])
        print(target_industries)
        if not date_str:
            return jsonify({"error": "No date provided"}), 400
        if not target_industries:
            return jsonify({"error": "No target industries provided"}), 400
            
        # Parse date string to datetime
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        print(target_date)
        # Retrieve emails from Gmail
        emails = gmail_service.get_emails_by_date(target_date)
        print(emails)
        if not emails:
            return jsonify({
                "message": "No emails found for the specified date",
                "digests": {}
            }), 200
            
        # Process emails and group by industry
        processed_data = process_emails(emails, target_industries)
        
        # Generate digests for each industry
        digests = generate_digest(processed_data)
        
        return jsonify({
            "message": "Success",
            "date": date_str,
            "total_emails": len(emails),
            "industries": target_industries,
            "digests": digests
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
