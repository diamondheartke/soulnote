# ava/tests/ava_conversation_tests.py

from django.contrib.auth import get_user_model
from ava.services.conversation_service import ConversationService

def main():
	username = input("Enter the django username or \'d\' for default: ")
	User = get_user_model()
	
	if username == 'd':
		username='DefaultUser'
		
	user = User.objects.get(username=username)
	
	service = ConversationService(user)
	
	print("---- Starting Ava ----")
	print("type \'exit\', \'stop\' or \'quit\' to stop the loop")
	while True:
		user_input = input("You> ")
		
		if user_input in ['exit', 'stop', 'quit']:
			print("Ava: Goodbye, till we meet again, beautiful soul!")
			break
		
		result = service.send_message(user_input)
	
		print("Conversation:", result["conversation_uuid"])
		print("Ava:", result["reply"])
		
if __name__ == '__main__':
	main()
	
