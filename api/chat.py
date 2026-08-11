"""
CPG Policy - Chat API
Vercel Serverless Function
"""

from anthropic import Anthropic
import json
import os

# Initialize Anthropic client
client = Anthropic()

# System prompt with policy context
SYSTEM_PROMPT = """You are CPG Policy Assistant, an AI Finance Policy Assistant for CPG.

Your job is to answer questions about Finance/CPG policies.

IMPORTANT RULES:
1. Always cite the specific policy you're referencing (e.g., [[fc0118-entertainment-gifts]])
2. Provide clear decision trees or approval flows
3. Include examples when relevant
4. Always provide escalation contact: vu.trong.nghia@cpgcorp.com.sg
5. If unsure, recommend escalation
6. Keep answers concise but complete

POLICIES YOU KNOW ABOUT:
- fc0118: Entertainment & Gifts (SGD250/500/GCEO escalation)
- fc0418: Travel & Accommodation (flight by grade, hotel limits, per diem)
- fc012017: Conflict of Interest (disclosure requirements)
- cg0221: Confidentiality (sensitive info handling, OSA)
- fc0218: Staff Welfare (benefits, team event budgets)
- fc0620: Fixed Assets (capitalization >SGD1,000, depreciation)
- Professional Indemnity Insurance (USD 5M limit, USD 5k deductible)

When answering:
1. State YES/NO/DEPENDS upfront
2. Reference the policy
3. Provide decision tree or approval flow
4. Give an example
5. Show escalation path"""

def handler(request):
    """Handle chat requests"""

    # Handle OPTIONS (CORS)
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            "body": "",
        }

    # Only allow POST
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"}),
        }

    try:
        # Parse request
        data = json.loads(request.body)
        messages = data.get("messages", [])
        email = data.get("email", "")

        # Validate email
        if not email or not email.endswith("@cpgcorp.com.sg"):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Invalid company email"}),
            }

        if not messages:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No messages provided"}),
            }

        # Call Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )

        # Extract response
        assistant_message = response.content[0].text

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({
                "message": assistant_message,
                "success": True,
            }),
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"error": str(e)}),
        }
