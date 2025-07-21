from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin(LoginRequiredMixin):
    required_roles = None  

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user_role = request.user.role

            if self.required_roles:
                # Normalize to list
                if isinstance(self.required_roles, str):
                    roles = [self.required_roles]
                else:
                    roles = self.required_roles

                if user_role not in roles:
                    raise PermissionDenied("You do not have permission to access this page.")

        return super().dispatch(request, *args, **kwargs)
