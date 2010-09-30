--
-- conference.sql
--
-- additional tables needed to store information about conferences
--

-- drop table conference_attendee;
drop table conference_community;
drop table presentation_project;
drop table presentation_person;
drop table conference_person;
drop table presentation;
drop table conference;

drop sequence conference_id_seq;
drop sequence presentation_id_seq;

create sequence conference_id_seq start 1 increment 1;
create sequence presentation_id_seq start 1 increment 1;

create table conference (
    conference_id int not null primary key default nextval('conference_id_seq'),
    name varchar(255) NOT NULL,
    start_date timestamp,
    stop_date timestamp,
    city varchar(255),
    country varchar(255),
    create_date timestamp not null default now()
);

create table conference_community (
    conference_id int not null references conference(conference_id),
    community_id int not null references community(community_id)
);

create table presentation (
    presentation_id int not null primary key default nextval('presentation_id_seq'),
    name varchar(255),
    start_date timestamp,
    stop_date timestamp,
    conference_id int not null references conference(conference_id),
    create_date timestamp not null default now()
);

create table presentation_project (
    presentation_id int not null references presentation(presentation_id),
    master_project_id int not null references master_project(master_project_id)
);


--
-- if we know someone was at a presentation
-- presenter is whether or not they presented at the presentation
--
create table presentation_person (
    presentation_id int not null references presentation(presentation_id),
    person_id int not null references person(person_id),
    presenter bool not null default 'F'
);


--
-- these are just people at a conference
--
create table conference_person (
    conference_id int not null references conference(conference_id),
    person_id int not null references person(person_id)
);

-- Generic statements to give everyone permissions
select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';

select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
