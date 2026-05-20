-- Supabase schema migration for E16 LMS.
-- Run this in the Supabase SQL Editor before syncing data from local SQLite.
-- The script is additive: it creates missing tables and adds missing columns.

create table if not exists public.users (
  id text primary key,
  email text not null unique,
  password_hash text not null,
  phone text,
  is_active boolean not null default true,
  role text not null,
  created_at timestamptz not null default now(),
  last_login timestamptz,
  login_count integer not null default 0,
  reset_token text unique,
  reset_token_expiry timestamptz
);

create table if not exists public.categories (
  id text primary key,
  name text not null,
  slug text not null unique,
  description text default '',
  icon text default '',
  sort_order integer default 0
);

create table if not exists public.courses (
  id text primary key,
  title text not null,
  short_description text not null default '',
  description text not null default '',
  cover_image_url text not null default '',
  total_lessons integer not null default 0,
  status text not null default 'draft',
  is_deleted boolean not null default false,
  category_id text references public.categories(id) on delete set null,
  teacher_id text not null references public.users(id) on delete cascade,
  rejection_note text,
  submitted_at timestamptz,
  published_at timestamptz,
  price integer not null default 250000,
  tags text not null default '',
  level text not null default '',
  created_at timestamptz not null default now()
);

create table if not exists public.system_settings (
  id text primary key,
  "key" text not null unique,
  "value" text,
  description text,
  updated_at timestamptz default now()
);

create table if not exists public.audit_logs (
  id text primary key,
  actor_id text references public.users(id) on delete set null,
  action text not null,
  target_type text,
  target_id text,
  detail text,
  ip_address text,
  created_at timestamptz default now()
);

create table if not exists public.lessons (
  id text primary key,
  course_id text not null references public.courses(id) on delete cascade,
  title text not null,
  video_url text not null default '',
  document_url text not null default '',
  sequence_order integer not null,
  created_at timestamptz not null default now()
);

create table if not exists public.enrollments (
  id text primary key,
  user_id text not null references public.users(id) on delete cascade,
  course_id text not null references public.courses(id) on delete cascade,
  enrolled_at timestamptz not null default now(),
  status text not null default 'active',
  constraint uq_enrollments_user_course unique (user_id, course_id)
);

create table if not exists public.learning_logs (
  log_id text primary key,
  user_id text not null references public.users(id) on delete cascade,
  lesson_id text not null references public.lessons(id) on delete cascade,
  action_type text not null,
  timestamp timestamptz not null default now()
);

create table if not exists public.quizzes (
  id text primary key,
  course_id text not null references public.courses(id) on delete cascade,
  title text not null,
  pass_score integer default 80,
  max_attempts integer default 3,
  time_limit integer,
  random_question_count integer default 0,
  due_date timestamptz,
  is_published boolean default false,
  created_at timestamptz default now()
);

create table if not exists public.questions (
  id text primary key,
  quiz_id text not null references public.quizzes(id) on delete cascade,
  text text not null,
  q_type text default 'mcq',
  sequence_order integer default 0
);

create table if not exists public.choices (
  id text primary key,
  question_id text not null references public.questions(id) on delete cascade,
  text text not null,
  is_correct boolean default false
);

create table if not exists public.quiz_attempts (
  id text primary key,
  quiz_id text not null references public.quizzes(id) on delete cascade,
  user_id text not null references public.users(id) on delete cascade,
  score integer,
  passed boolean,
  attempted_at timestamptz default now(),
  completed_at timestamptz
);

create table if not exists public.quiz_answers (
  id text primary key,
  attempt_id text not null references public.quiz_attempts(id) on delete cascade,
  question_id text not null references public.questions(id) on delete cascade,
  choice_id text references public.choices(id) on delete cascade,
  text_answer text
);

create table if not exists public.assignments (
  id text primary key,
  course_id text not null references public.courses(id) on delete cascade,
  title text not null,
  description text not null,
  deadline timestamptz,
  allow_file boolean default true,
  allow_text boolean default true,
  created_at timestamptz default now()
);

create table if not exists public.submissions (
  id text primary key,
  assignment_id text not null references public.assignments(id) on delete cascade,
  user_id text not null references public.users(id) on delete cascade,
  text_content text,
  file_path text,
  submitted_at timestamptz default now(),
  status text default 'pending',
  score integer,
  feedback text,
  graded_at timestamptz,
  graded_by text references public.users(id) on delete set null,
  constraint uq_submissions_user_assignment unique (user_id, assignment_id)
);

create table if not exists public.notifications (
  id text primary key,
  user_id text not null references public.users(id) on delete cascade,
  type text not null,
  message text not null,
  link text,
  is_read boolean default false,
  created_at timestamptz default now()
);

create table if not exists public.announcements (
  id text primary key,
  course_id text not null references public.courses(id) on delete cascade,
  author_id text not null references public.users(id) on delete cascade,
  title text not null,
  body text not null,
  is_pinned boolean default false,
  created_at timestamptz default now()
);

create table if not exists public.forum_threads (
  id text primary key,
  course_id text not null references public.courses(id) on delete cascade,
  author_id text not null references public.users(id) on delete cascade,
  title text not null,
  body text not null,
  is_pinned boolean default false,
  is_hidden boolean not null default false,
  created_at timestamptz default now()
);

create table if not exists public.forum_replies (
  id text primary key,
  thread_id text not null references public.forum_threads(id) on delete cascade,
  author_id text not null references public.users(id) on delete cascade,
  body text not null,
  is_hidden boolean not null default false,
  created_at timestamptz default now()
);

create table if not exists public.certificates (
  id text primary key,
  user_id text not null references public.users(id) on delete cascade,
  course_id text not null references public.courses(id) on delete cascade,
  cert_code text unique,
  issued_at timestamptz default now(),
  constraint uq_certificates_user_course unique (user_id, course_id)
);

alter table public.users
  add column if not exists phone text,
  add column if not exists is_active boolean not null default true,
  add column if not exists last_login timestamptz,
  add column if not exists login_count integer not null default 0,
  add column if not exists reset_token text,
  add column if not exists reset_token_expiry timestamptz;

alter table public.courses
  add column if not exists short_description text not null default '',
  add column if not exists status text not null default 'draft',
  add column if not exists is_deleted boolean not null default false,
  add column if not exists category_id text,
  add column if not exists rejection_note text,
  add column if not exists submitted_at timestamptz,
  add column if not exists published_at timestamptz,
  add column if not exists price integer not null default 250000,
  add column if not exists tags text not null default '',
  add column if not exists level text not null default '';

alter table public.quizzes
  add column if not exists time_limit integer,
  add column if not exists random_question_count integer default 0,
  add column if not exists due_date timestamptz;

create index if not exists ix_users_role on public.users(role);
create index if not exists ix_courses_status on public.courses(status);
create index if not exists ix_courses_is_deleted on public.courses(is_deleted);
create index if not exists ix_courses_teacher_id on public.courses(teacher_id);
create index if not exists ix_lessons_course_id on public.lessons(course_id);
create index if not exists ix_enrollments_user_id on public.enrollments(user_id);
create index if not exists ix_enrollments_course_id on public.enrollments(course_id);
create index if not exists ix_learning_logs_user_id on public.learning_logs(user_id);
create index if not exists ix_learning_logs_lesson_id on public.learning_logs(lesson_id);
create index if not exists ix_learning_logs_timestamp on public.learning_logs(timestamp);
create index if not exists ix_quizzes_course_id on public.quizzes(course_id);
create index if not exists ix_questions_quiz_id on public.questions(quiz_id);
create index if not exists ix_choices_question_id on public.choices(question_id);
create index if not exists ix_quiz_attempts_quiz_id on public.quiz_attempts(quiz_id);
create index if not exists ix_quiz_attempts_user_id on public.quiz_attempts(user_id);
