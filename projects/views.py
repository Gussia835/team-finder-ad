import json

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ProjectForm
from .models import Project, ProjectSkill


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Project.objects.filter(status='open')
            .select_related('owner')
            .prefetch_related('skills', 'participants')
        )
        skill = self.request.GET.get('skill')
        if skill:
            qs = qs.filter(skills__name__iexact=skill).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = ProjectSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get('skill')
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query_prefix'] = params.urlencode()
        if context['query_prefix']:
            context['query_prefix'] += '&'
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

    def get_queryset(self):
        return Project.objects.select_related('owner').prefetch_related(
            'participants',
            'skills',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        project = self.object
        context['is_owner'] = user.is_authenticated and project.owner_id == user.pk
        context['is_participant'] = (
            user.is_authenticated
            and project.participants.filter(pk=user.pk).exists()
        )
        if user.is_authenticated:
            context['is_favorite'] = user.favorites.filter(pk=project.pk).exists()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = False
        return context

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user
        project.save()
        project.participants.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def test_func(self):
        return self.get_object().owner_id == self.request.user.pk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class FavoriteProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'
    paginate_by = 12

    def get_queryset(self):
        return (
            self.request.user.favorites.all()
            .select_related('owner')
            .prefetch_related('skills')
            .order_by('-created_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        context['query_prefix'] = params.urlencode()
        if context['query_prefix']:
            context['query_prefix'] += '&'
        return context


def _json_body(request):
    if request.body:
        try:
            return json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return {}
    return {}


@login_required
@require_POST
def toggle_favorite(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    favorited = False
    if user.favorites.filter(pk=project.pk).exists():
        user.favorites.remove(project)
    else:
        user.favorites.add(project)
        favorited = True
    return JsonResponse({'status': 'ok', 'favorited': favorited})


@login_required
@require_POST
def complete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.pk or project.status != 'open':
        return JsonResponse({'status': 'error'}, status=403)
    project.complete()
    return JsonResponse({'status': 'ok', 'project_status': 'closed'})


@login_required
@require_POST
def toggle_participate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    user = request.user
    if project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
        return JsonResponse({'status': 'ok', 'participant': False})
    project.participants.add(user)
    return JsonResponse({'status': 'ok', 'participant': True})


def skills_autocomplete(request):
    q = request.GET.get('q', '')
    skills = (
        ProjectSkill.objects.filter(name__istartswith=q)
        .order_by('name')[:10]
    )
    data = [{'id': s.id, 'name': s.name} for s in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.pk:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    body = _json_body(request)
    skill_id = body.get('skill_id')
    name = (body.get('name') or '').strip()

    if skill_id:
        skill = get_object_or_404(ProjectSkill, pk=skill_id)
        created = False
    elif name:
        skill, created = ProjectSkill.objects.get_or_create(name=name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=400)

    added = False
    if not project.skills.filter(pk=skill.pk).exists():
        project.skills.add(skill)
        added = True

    status_code = 201 if created else 200
    return JsonResponse(
        {
            'skill_id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added,
        },
        status=status_code,
    )


@login_required
@require_POST
def remove_project_skill(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    skill = get_object_or_404(ProjectSkill, pk=skill_id)
    if project.owner_id != request.user.pk:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    project.skills.remove(skill)
    return JsonResponse({'status': 'ok'})
