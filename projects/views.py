from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from team_finder.constants import QueryParam
from team_finder.utils.http import parse_json_body
from team_finder.utils.mixins import QueryPrefixContextMixin
from team_finder.utils.skills import autocomplete_query
from projects.constants import (
    PROJECTS_PER_PAGE,
    TEMPLATE_CREATE_PROJECT,
    TEMPLATE_FAVORITE_PROJECTS,
    TEMPLATE_PROJECT_DETAILS,
    TEMPLATE_PROJECT_LIST,
)
from projects.forms import ProjectForm
from projects.models import Project, ProjectSkill
from projects.services import (
    add_project_skill,
    complete_project,
    filter_projects_by_skill,
    open_projects_queryset,
    project_skills_autocomplete,
    remove_project_skill,
    toggle_favorite,
    toggle_participation,
)


class ProjectListView(QueryPrefixContextMixin,
                      ListView):
    model = Project
    template_name = TEMPLATE_PROJECT_LIST
    context_object_name = 'projects'
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        qs = open_projects_queryset()
        skill = self.request.GET.get(QueryParam.SKILL)
        return filter_projects_by_skill(qs, skill)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_skills'] = ProjectSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get(QueryParam.SKILL)
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = TEMPLATE_PROJECT_DETAILS
    context_object_name = 'project'

    def get_queryset(self):
        return open_projects_queryset(ignore_status=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        project = self.object
        context['is_owner'] = (
            user.is_authenticated and project.owner_id == user.pk
        )
        context['is_participant'] = (
            user.is_authenticated
            and project.participants.filter(pk=user.pk).exists()
        )
        if user.is_authenticated:
            context['is_favorite'] = user.favorites.filter(
                pk=project.pk,
            ).exists()
        return context


class ProjectCreateView(LoginRequiredMixin,
                        CreateView):
    model = Project
    form_class = ProjectForm
    template_name = TEMPLATE_CREATE_PROJECT

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
        return reverse('projects:detail',
                       kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin,
                        UserPassesTestMixin,
                        UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = TEMPLATE_CREATE_PROJECT

    def test_func(self):
        return self.get_object().owner_id == self.request.user.pk

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse('projects:detail',
                       kwargs={'pk': self.object.pk})


class FavoriteProjectsView(LoginRequiredMixin,
                           QueryPrefixContextMixin,
                           ListView):
    model = Project
    template_name = TEMPLATE_FAVORITE_PROJECTS
    context_object_name = 'projects'
    paginate_by = PROJECTS_PER_PAGE

    def get_queryset(self):
        return (
            self.request.user.favorites.all()
            .select_related('owner')
            .prefetch_related('skills')
            .order_by('-created_at')
        )


@login_required
@require_POST
def toggle_favorite_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return toggle_favorite(request.user, project)


@login_required
@require_POST
def complete_project_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return complete_project(project, request.user)


@login_required
@require_POST
def toggle_participate_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return toggle_participation(project, request.user)


def skills_autocomplete(request):
    data = project_skills_autocomplete(autocomplete_query(request))
    return JsonResponse(data, safe=False)


@login_required
@require_POST
def add_project_skill_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return add_project_skill(
        project,
        request.user,
        parse_json_body(request),
    )


@login_required
@require_POST
def remove_project_skill_view(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk)
    skill = get_object_or_404(ProjectSkill, pk=skill_id)
    return remove_project_skill(project, request.user, skill)
