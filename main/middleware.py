from datetime import datetime, timedelta
from django.conf import settings # type: ignore
from django.shortcuts import redirect # type: ignore

class LockScreenActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get the last activity time from the session
            last_activity = request.session.get('last_activity')
            now = datetime.now()

            # Check if there is a last activity time
            if last_activity:
                elapsed_time = now - datetime.strptime(last_activity, '%Y-%m-%d %H:%M:%S.%f')
                # Check if the elapsed time exceeds the session cookie age
                if elapsed_time > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                    request.session['locked'] = True  # Lock the session
                    return redirect('lockscreen')  # Redirect to lock screen

            # Update the last activity time in the session
            request.session['last_activity'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')
            request.session['locked'] = False  # Ensure the session is marked as unlocked
            
            # Check if the session is locked
            if request.session.get('locked', True):
                if request.path != '/lockscreen':  # Adjust the URL as necessary
                    return redirect('/lockscreen')  # Redirect to the lock screen

        response = self.get_response(request)
        return response