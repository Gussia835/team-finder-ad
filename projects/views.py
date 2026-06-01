from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .models import Project, ProjectSkill
from .forms import ProjectForm


print('projects.views')

class ProjectListView(ListView):
    '''список открытых проектов'''
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 12
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Project.objects.filter(
            Q(status='open') | Q(status='Open')
        ).select_related('owner').prefetch_related('skills')

        # вариант 3
        if skill := self.request.GET.get('skill'):
            qs = qs.filter(skills__name__iexact=skill).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # вариант 3
        context['all_skills'] = ProjectSkill.objects.all().order_by('name')
        context['active_skill'] = self.request.GET.get('skill')
        return context


class ProjectDetailView(DetailView):
    '''детальный проект'''
    model = Project
    template_name = 'projects/project-details.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        project = self.object

        context['is_owner'] = project.owner == user
        context['is_participant'] = (
            user.is_authenticated and
            project.participants.filter(pk=user.pk).exists()
        )
        # вариант 1
        if user.is_authenticated:
            context['is_favorite'] = user.favorites.filter(pk=project.pk
                                                           ).exists()
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    '''создание нового проекта'''
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        project = form.save(commit=False)
        project.owner = self.request.user

        project.save()

        project.participants.add(self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''редактирование проекта'''
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})


# вариант 1
class FavoriteProjectsView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/favorite_projects.html'
    context_object_name = 'projects'
    paginate_by = 12
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            self.request.user.favorites
            .select_related('owner')
            .prefetch_related('skills')
        )
