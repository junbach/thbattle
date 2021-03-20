# Generated by Django 3.1.7 on 2021-03-20 09:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import player.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('badge', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('phone', models.CharField(help_text='手机号', max_length=15, unique=True, validators=[player.models.is_phone_number], verbose_name='手机号')),
                ('is_staff', models.BooleanField(default=False, help_text='是否可以登录后台', verbose_name='职员状态')),
                ('is_active', models.BooleanField(default=True, help_text='指明用户是否被认为活跃的。以反选代替删除帐号。', verbose_name='启用帐号')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, help_text='加入日期', verbose_name='加入日期')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': '用户',
                'verbose_name_plural': '用户',
            },
            managers=[
                ('objects', player.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='昵称', max_length=15, unique=True, validators=[player.models.is_name], verbose_name='昵称')),
                ('bio', models.CharField(blank=True, help_text='签名', max_length=150, verbose_name='签名')),
                ('avatar', models.URLField(blank=True, help_text='头像', max_length=150, verbose_name='头像')),
                ('prefs', models.TextField(blank=True, help_text='个人设置', verbose_name='个人设置')),
                ('point', models.IntegerField(default=0, help_text='点', verbose_name='点')),
                ('power', models.IntegerField(default=0, help_text='P', verbose_name='P')),
                ('bomb', models.IntegerField(default=0, help_text='B', verbose_name='B')),
                ('full', models.IntegerField(default=0, help_text='F', verbose_name='F')),
                ('up', models.IntegerField(default=0, help_text='+1UP', verbose_name='+1UP')),
                ('games', models.IntegerField(default=0, help_text='游戏数', verbose_name='游戏数')),
                ('drops', models.IntegerField(default=0, help_text='逃跑数', verbose_name='逃跑数')),
                ('badges', models.ManyToManyField(blank=True, help_text='勋章', related_name='players', to='badge.Badge', verbose_name='勋章')),
                ('blocks', models.ManyToManyField(blank=True, help_text='黑名单', related_name='blocked_by', to='player.Player', verbose_name='黑名单')),
                ('friends', models.ManyToManyField(blank=True, help_text='好友', related_name='friended_by', to='player.Player', verbose_name='好友')),
                ('user', models.OneToOneField(help_text='关联用户', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '玩家',
                'verbose_name_plural': '玩家',
                'permissions': (('change_credit', '可以修改积分'),),
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(help_text='原因', max_length=10, verbose_name='原因')),
                ('detail', models.TextField(help_text='原因', verbose_name='详情')),
                ('game_id', models.IntegerField(blank=True, help_text='游戏ID', null=True, verbose_name='游戏ID')),
                ('reported_at', models.DateTimeField(default=django.utils.timezone.now, help_text='举报时间', verbose_name='举报时间')),
                ('outcome', models.CharField(blank=True, help_text='处理结果', max_length=150, null=True, verbose_name='处理结果')),
                ('reporter', models.ForeignKey(help_text='举报者', on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='player.player', verbose_name='举报者')),
                ('suspect', models.ForeignKey(help_text='嫌疑人', on_delete=django.db.models.deletion.CASCADE, related_name='reported_by', to='player.player', verbose_name='嫌疑人')),
            ],
            options={
                'verbose_name': '举报',
                'verbose_name_plural': '举报',
            },
        ),
    ]
