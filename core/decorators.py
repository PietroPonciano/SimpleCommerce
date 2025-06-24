from django.shortcuts import redirect
from functools import wraps

def staff_required_redirect(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('acesso_negado')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
