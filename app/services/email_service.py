import logging
import os
import time
from typing import Optional, Dict, Any

import dns.resolver
import requests
from jinja2 import Environment, FileSystemLoader
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.monitoring import handle_error

logger = logging.getLogger(__name__)

class DNSEnforcedSession(requests.Session):
	"""Custom session class with enhanced DNS resolution for Kubernetes environments"""
	def __init__(self, *args, **kwargs):
		super().__init__()
		self.resolver = self._configure_dns()
		
		# Configure retry strategy
		retry_strategy = Retry(
			total=3,  # total number of retries
			backoff_factor=1,  # wait 1, 2, 4 seconds between retries
			status_forcelist=[408, 429, 500, 502, 503, 504],
			allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
		)
		adapter = HTTPAdapter(max_retries=retry_strategy)
		self.mount("https://", adapter)

	@staticmethod
	def _configure_dns():
		"""Configure DNS resolver with Kubernetes settings"""
		try:
			resolver = dns.resolver.Resolver()
			
			# Get DNS settings from resolv.conf
			nameservers = []
			with open('/etc/resolv.conf', 'r') as f:
				for line in f:
					if line.startswith('nameserver'):
						nameservers.append(line.split()[1])
			
			if nameservers:
				resolver.nameservers = nameservers
				logger.info(f"Configured DNS nameservers: {nameservers}")
				
				# Add common Kubernetes search domains
				resolver.search = [
					'svc.cluster.local',
					'cluster.local',
					'c.kinsta-app-hosting.internal',
					'google.internal'
				]
				
			return resolver
		except Exception as e:
			logger.error(f"Error configuring DNS resolver: {e}")
			return None

	def send(self, request, **kwargs):
		"""Override send to implement custom DNS resolution"""
		try:
			url_parts = requests.utils.urlparse(request.url)
			if url_parts.hostname and self.resolver:
				try:
					# Try DNS resolution
					answers = self.resolver.resolve(url_parts.hostname, 'A')
					ip = answers[0].address
					logger.info(f"Resolved {url_parts.hostname} to {ip}")
					
					# Replace hostname with IP in URL
					new_url = request.url.replace(url_parts.hostname, ip)
					request.url = new_url
					
					# Preserve original hostname in headers
					request.headers['Host'] = url_parts.hostname
				except Exception as e:
					logger.warning(f"DNS resolution failed for {url_parts.hostname}: {e}")
					# Continue with original URL if resolution fails
		except Exception as e:
			logger.error(f"Error in custom DNS resolution: {e}")
		
		return super().send(request, **kwargs)

class EmailService:
	"""Email service using SendLayer with enhanced DNS resolution and templates"""
	
	def __init__(self):
		self.api_key = os.getenv("SENDLAYER_API_KEY")
		if not self.api_key:
			raise ValueError("SENDLAYER_API_KEY environment variable is not set")
			
		# Email configuration
		self.default_from_email = os.getenv("DEFAULT_FROM_EMAIL", "info@rosedalemassage.co.uk")
		self.default_reply_to = os.getenv("DEFAULT_REPLY_TO", "bookings@rosedalemassage.co.uk")
		
		# URL configuration
		self.booking_url = os.getenv("BOOKING_URL", "https://booking.rosedalemassage.co.uk")
		self.tracking_base_url = os.getenv("TRACKING_BASE_URL", "https://www.royalmail.com/track-your-item#/tracking/")
		
		self.session = DNSEnforcedSession()
		
		# Initialize Jinja2 environment for templates
		template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'email')
		self.jinja_env = Environment(
			loader=FileSystemLoader(template_dir),
			autoescape=True
		)
		
		# Configure session headers
		self.session.headers.update({
			"Authorization": f"Bearer {self.api_key}",
			"Content-Type": "application/json",
			"User-Agent": "RosedaleMassage/1.0"
		})

	def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
		"""Render an HTML template with the given context"""
		try:
			# Load the template
			template = self.jinja_env.get_template(f"{template_name}.html")
			
			# Add any global context values
			context.update({
				"booking_url": self.booking_url,
				"support_email": self.default_reply_to,
				"website_url": "https://www.rosedalemassage.co.uk"
			})
			
			# Render the template
			return template.render(**context)
		except Exception as e:
			error_context = f"Failed to render template: {template_name}"
			handle_error(e, error_context)
			raise
			
	def send_email(
		self,
		to_email: str,
		subject: str,
		html_content: str,
		from_email: Optional[str] = None,
		reply_to: Optional[str] = None,
		cc: Optional[list] = None,
		bcc: Optional[list] = None,
		track_opens: bool = True,
		track_clicks: bool = True
	) -> Dict[str, Any]:
		"""Send an email using SendLayer"""
		try:
			url = "https://api.sendlayer.com/v1/emails"
			
			data = {
				"from": from_email or self.default_from_email,
				"reply_to": reply_to or self.default_reply_to,  # Always include reply-to
				"to": to_email,
				"subject": subject,
				"html": html_content,
				"track_opens": track_opens,
				"track_clicks": track_clicks
			}
			
			if cc:
				data["cc"] = cc
			if bcc:
				data["bcc"] = bcc
	
			start_time = time.time()
			logger.info(f"Attempting to send email to {to_email}")
			
			response = self.session.post(url, json=data, timeout=30)
			duration = time.time() - start_time
			
			logger.info(f"SendLayer API call took {duration:.2f} seconds")
			
			if response.status_code == 200:
				logger.info(f"Successfully sent email to {to_email}")
				return response.json()
			else:
				logger.error(f"Failed to send email. Status: {response.status_code}")
				logger.error(f"Response: {response.text}")
				response.raise_for_status()
				
		except requests.exceptions.RequestException as e:
			error_context = f"Failed to send email to {to_email} (subject: {subject})"
			handle_error(e, error_context)
			raise
		except Exception as e:
			error_context = f"Unexpected error sending email to {to_email}"
			handle_error(e, error_context)
			raise
		finally:
			self.session.close()

	def send_gift_card_email(
		self,
		to_email: str,
		template_type: str,
		context: Dict[str, Any],
		from_email: Optional[str] = None,
		reply_to: Optional[str] = None,
		tracking_number: Optional[str] = None
	) -> Dict[str, Any]:
		"""Send a gift card email using a specific template.
	
		Args:
			to_email: Customer's email address
			template_type: Type of gift card email ('digital_gift_card', 'premium_gift_card', 'unlimited_package')
			context: Template variables (must include: name, amount, etc.)
			from_email: Optional sender email (defaults to DEFAULT_FROM_EMAIL)
			reply_to: Optional reply-to address (defaults to template-specific address)
			tracking_number: Optional tracking number for premium gift cards
	
		Returns:
			Dict containing SendLayer API response
	
		Raises:
			ValueError: If template_type is invalid
			RequestException: If email sending fails
		"""
		# Add tracking URL if tracking number provided
		if tracking_number and template_type == 'premium_gift_card':
			context['tracking_url'] = f"{self.tracking_base_url}{tracking_number}"
		
		allowed_templates = {
			'digital_gift_card': {
				'subject': 'Digital Gift Card Purchase Confirmation',
				'reply_to': 'giftcards@rosedalemassage.co.uk'
			},
			'premium_gift_card': {
				'subject': 'Premium Gift Card Purchase Confirmation',
				'reply_to': 'giftcards@rosedalemassage.co.uk'
			},
			'unlimited_package': {
				'subject': 'Welcome to Unlimited Massage Membership',
				'reply_to': 'membership@rosedalemassage.co.uk'
			}
		}
		
		if template_type not in allowed_templates:
			raise ValueError(f"Invalid template type. Must be one of: {', '.join(allowed_templates.keys())}")
		
		template_config = allowed_templates[template_type]
		html_content = self._render_template(template_type, context)
		
		return self.send_email(
			to_email=to_email,
			subject=template_config['subject'],
			html_content=html_content,
			from_email=from_email,
			reply_to=reply_to or template_config['reply_to']
		)

	def send_welcome_email(
		self,
		to_email: str,
		name: str,
		newsletter_subscribed: bool = False,
		from_email: Optional[str] = None,
		reply_to: Optional[str] = None
	) -> Dict[str, Any]:
		"""
		Send a welcome email to new customers
		
		Args:
			to_email: Customer's email address
			name: Customer's name
			newsletter_subscribed: Boolean indicating if already subscribed
			from_email: Optional sender email
			reply_to: Optional reply-to address
		"""
		context = {
			"name": name,
			"newsletter_subscribed": newsletter_subscribed,
			"newsletter_signup_url": f"{os.getenv('NEWSLETTER_SIGNUP_URL', 'https://rosedalemassage.co.uk/newsletter')}?email={to_email}",
			"booking_url": self.booking_url
		}
	
		html_content = self._render_template('welcome_customer', context)
		
		return self.send_email(
			to_email=to_email,
			subject="Welcome to Rosedale Massage",
			html_content=html_content,
			from_email=from_email,
			reply_to=reply_to or "hello@rosedalemassage.co.uk"
		)
	
	# Example usage:
	"""
	email_service = EmailService()
	
	try:
		result = email_service.send_welcome_email(
			to_email="emma@example.com",
			name="Emma",
			newsletter_subscribed=False
		)
		print("Welcome email sent successfully")
	
	except Exception as e:
		print(f"Failed to send welcome email: {str(e)}")
	"""