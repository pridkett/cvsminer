-- bugscraper.sql
--
-- create the tables for the bugscraper script

drop table bug_comment cascade;
drop table bug cascade;
drop table bug_severity cascade;
drop table bug_status cascade;
drop table bug_priority cascade;
drop table bug_resolution cascade;

drop sequence bug_status_id_seq;
drop sequence bug_id_seq;
drop sequence bug_comment_id_seq;
drop sequence bug_severity_id_seq;
drop sequence bug_priority_id_seq;
drop sequence bug_resolution_id_seq;

create sequence bug_status_id_seq start 1 increment 1;
create sequence bug_id_seq start 1 increment 1;
create sequence bug_comment_id_seq start 1 increment 1;
create sequence bug_severity_id_seq start 1 increment 1;
create sequence bug_priority_id_seq start 1 increment 1;
create sequence bug_resolution_id_seq start 1 increment 1;

create table bug_resolution (
    bug_resolution_id int not null primary key default nextval('bug_resolution_id_seq'),
    bug_resolution_desc varchar(64) not null
);

create table bug_status (
    bug_status_id int not null primary key default nextval('bug_status_id_seq'),
    bug_status_desc varchar(64) not null
);

create table bug_severity (
    bug_severity_id int not null primary key default nextval('bug_severity_id_seq'),
    bug_severity_desc varchar(64) not null
);

create table bug_priority (
    bug_priority_id int not null primary key default nextval('bug_priority_id_seq'),
    bug_priority_desc varchar(64) not null
);

create table bug (
    id int not null primary key default nextval('bug_id_seq'),
    bug_id int not null,
    project_id int not null references master_project(master_project_id),
    bug_status_id int not null references bug_status(bug_status_id),
    priority_id int not null references bug_priority(bug_priority_id),
    resolution_id int references bug_resolution(bug_resolution_id),
    severity_id int references bug_severity(bug_severity_id),
    assigned_to varchar(255),
    reporter varchar(255),
    qa_contact varchar(255),
    short_desc text,
    create_date timestamp,
    delta_date timestamp
);
create index bug_bug_id_idx on bug(bug_id);
create index bug_project_id_idx on bug(project_id);

create table bug_comment (
    bug_comment_id int not null primary key default nextval('bug_comment_id_seq'),
    bug_id int not null references bug(id),
    comment_text text not null,
    comment_author varchar(255) not null,
    comment_date timestamp not null,
    comment_seq int not null
);
create index bug_comment_bug_id_idx on bug_comment(bug_id);

-- Grant permissions to everyone
select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
