from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404
from django.shortcuts import redirect, resolve_url, render, get_object_or_404
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from .forms import (
    LoginForm, UserCreateForm, UserUpdateForm, MyPasswordChangeForm,
    MyPasswordResetForm, MySetPasswordForm, PersonForm, CostForm
)
from cms.models import Person, Cost

User = get_user_model()


class Top(LoginRequiredMixin, generic.TemplateView):
    template_name = 'cms/top.html'


class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'cms/login.html'


class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'cms/login.html'


class UserCreate(generic.CreateView):
    """ユーザー仮登録"""
    template_name = 'cms/user_create.html'
    form_class = UserCreateForm

    def form_valid(self, form):
        """仮登録と本登録用メールの発行."""
        # 仮登録と本登録の切り替えは、is_active属性を使うと簡単です。
        # 退会処理も、is_activeをFalseにするだけにしておくと捗ります。
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # 管理サイトのパスワードリセットの際に行っている処理とほぼ同じ
        current_site = get_current_site(self.request)
        domain = current_site.domain
        context = {
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': domain,
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)).decode('utf-8'),
            'token': urlsafe_base64_encode(force_bytes(user.email)).decode('utf-8'),
            'user': user,
        }

        subject_template = get_template('cms/mail_template/create/subject.txt')
        subject = subject_template.render(context)

        message_template = get_template('cms/mail_template/create/message.txt')
        message = message_template.render(context)

        user.email_user(subject, message)
        return redirect('cms:user_create_done')


class UserCreateDone(generic.TemplateView):
    """ユーザー仮登録したよ"""
    template_name = 'cms/user_create_done.html'


class UserCreateComplete(generic.TemplateView):
    """メール内URLアクセス後のユーザー本登録"""
    template_name = 'cms/user_create_complete.html'

    def get(self, request, **kwargs):
        """uid、tokenが正しければ本登録."""
        token = kwargs.get('token')
        uidb64 = kwargs.get('uidb64')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            email = force_text(urlsafe_base64_decode(token))
            user = User.objects.get(pk=uid, email=email)
            if user.is_active:
                raise Http404
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        else:
            user.is_active = True
            user.save()
            return super().get(request, **kwargs)

        raise Http404


class OnlyYouMixin(LoginRequiredMixin, UserPassesTestMixin):
    """本人か、スーパーユーザーだけユーザーページアクセスを許可する"""
    raise_exception = True

    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser


class UserDetail(OnlyYouMixin, generic.DetailView):
    """ユーザーの詳細ページ"""
    model = User
    template_name = 'cms/user_detail.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く


class UserUpdate(OnlyYouMixin, generic.UpdateView):
    """ユーザー情報更新ページ"""
    model = User
    form_class = UserUpdateForm
    template_name = 'cms/user_form.html'  # デフォルトユーザーを使う場合に備え、きちんとtemplate名を書く

    def get_success_url(self):
        return resolve_url('cms:user_detail', pk=self.kwargs['pk'])


class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    success_url = reverse_lazy('cms:password_change_done')
    template_name = 'cms/password_change.html'


class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'cms/password_change_done.html'


class PasswordReset(LoginRequiredMixin, PasswordResetView):
    """パスワード変更用URLの送付ページ"""
    subject_template_name = 'cms/mail_template/reset/subject.txt'
    email_template_name = 'cms/mail_template/reset/message.txt'
    template_name = 'cms/password_reset_form.html'
    form_class = MyPasswordResetForm
    success_url = reverse_lazy('cms:password_reset_done')


class PasswordResetDone(LoginRequiredMixin, PasswordResetDoneView):
    """パスワード変更用URLを送りましたページ"""
    template_name = 'cms/password_reset_done.html'


class PasswordResetConfirm(LoginRequiredMixin, PasswordResetConfirmView):
    """新パスワード入力ページ"""
    form_class = MySetPasswordForm
    success_url = reverse_lazy('cms:password_reset_complete')
    template_name = 'cms/password_reset_confirm.html'


class PasswordResetComplete(LoginRequiredMixin, PasswordResetCompleteView):
    """新パスワード設定しましたページ"""
    template_name = 'cms/password_reset_complete.html'


class PersonList(LoginRequiredMixin, generic.TemplateView):

    def person_list(request):
        """要員の一覧"""
        persons = Person.objects.all().order_by('id')
        return render(request,
                      'cms/person_list.html',     # 使用するテンプレート
                      {'persons': persons})         # テンプレートに渡すデータ

    def person_edit(request, person_id=None):
        """要員の編集"""
    #     return HttpResponse('要員の編集')
        if person_id:   # person_id が指定されている (修正時)
            person = get_object_or_404(Person, pk=person_id)
        else:         # person_id が指定されていない (追加時)
            person = Person()

        if request.method == 'POST':
            form = PersonForm(request.POST, instance=person)  # POST された request データからフォームを作成
            if form.is_valid():    # フォームのバリデーション
                person = form.save(commit=False)
                person.save()
                return redirect('cms:person_list')
        else:    # GET の時
            form = PersonForm(instance=person)  # person インスタンスからフォームを作成

        return render(request, 'cms/person_edit.html', dict(form=form, person_id=person_id))

    def person_del(request, person_id):
        """要員の削除"""
    #     return HttpResponse('要員の削除')
        person = get_object_or_404(Person, pk=person_id)
        person.delete()
        return redirect('cms:person_list')


class CostList(LoginRequiredMixin, generic.TemplateView):
    """コストの一覧"""
    context_object_name='costs'
    template_name='cms/cost_list.html'
    paginate_by = 2  # １ページは最大2件ずつでページングする

    def cost_list(request, person_id):
        """コストの一覧"""
        person = Person.objects.get(pk=person_id)
        Cost.person = person

        costs = Cost.objects.all().order_by('id')
        return render(request,
                      'cms/cost_list.html',     # 使用するテンプレート
                      {'costs': costs, 'person': person})         # テンプレートに渡すデータ

    def cost_edit(request, person_id, cost_id=None):
        """感想の編集"""
        person = get_object_or_404(Person, pk=person_id)  # 親の書籍を読む
        if cost_id:  # cost_id が指定されている (修正時)
            cost = get_object_or_404(Cost, pk=cost_id)
        else:  # cost_id が指定されていない (追加時)
            cost = Cost()

        if request.method == 'POST':
            form = CostForm(request.POST, instance=cost)  # POST された request データからフォームを作成
            if form.is_valid():  # フォームのバリデーション
                cost = form.save(commit=False)
                cost.person = person  # この感想の、親の書籍をセット
                cost.save()
                return redirect('cms:cost_list', person_id=person_id)
        else:  # GET の時
            form = CostForm(instance=cost)  # cost インスタンスからフォームを作成

        return render(request,
                      'cms/cost_edit.html',
                      dict(form=form, person_id=person_id, cost_id=cost_id))

    def cost_del(request, person_id, cost_id):
        """感想の削除"""
        cost = get_object_or_404(Cost, pk=cost_id)
        cost.delete()
        return redirect('cms:cost_list', person_id=person_id)