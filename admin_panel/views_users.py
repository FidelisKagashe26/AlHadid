from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from .forms import AdminUserCreateForm, AdminUserUpdateForm, AdminSetPasswordForm


@login_required
@permission_required('auth.view_user', raise_exception=True)
def users_list(request):
    q = request.GET.get('q', '').strip()
    users = User.objects.filter(is_staff=True)
    if q:
        users = users.filter(username__icontains=q)
    return render(request, 'admin_panel/users_list.html', {
        'users': users.order_by('-is_superuser', 'username'),
        'q': q,
    })


@login_required
@permission_required('auth.add_user', raise_exception=True)
def users_create(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if not user.is_staff:
                user.is_staff = True
            user.save()
            form.save_m2m()  # groups
            messages.success(request, 'Admin user created successfully.')
            return redirect('admin_panel:admin_users_list')
    else:
        form = AdminUserCreateForm()
    return render(request, 'admin_panel/user_form.html', {'form': form, 'mode': 'create'})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def users_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin user updated successfully.')
            return redirect('admin_panel:admin_users_list')
    else:
        form = AdminUserUpdateForm(instance=user)
    return render(request, 'admin_panel/user_form.html', {'form': form, 'mode': 'update', 'user_obj': user})


@login_required
@permission_required('auth.delete_user', raise_exception=True)
def users_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if request.user == user:
            messages.error(request, "You can't delete yourself.")
        else:
            user.delete()
            messages.success(request, 'Admin user deleted.')
            return redirect('admin_panel:admin_users_list')
    return render(request, 'admin_panel/user_confirm_delete.html', {'user_obj': user})


@login_required
@permission_required('auth.change_user', raise_exception=True)
def users_set_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Password updated for {user.username}.")
            return redirect('admin_panel:admin_users_list')
    else:
        form = AdminSetPasswordForm(user)
    return render(request, 'admin_panel/user_set_password.html', {'form': form, 'user_obj': user})


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was updated.')
            return redirect('admin_panel:dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'admin_panel/password_change.html', {'form': form})
