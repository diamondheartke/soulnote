from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def ava_chat_view(request):
	"""
    Renders Ava's conversational interface.

    Authentication is required because Ava is a private
    companion inside the SoulNote application.
    """
	context = {
		'user': request.user,
	}

	return render(request, 'ava/index.html', context)
