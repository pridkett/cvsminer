--
-- study.sql
--
-- files to store information about studies, really just a simple helper
-- table so we have everything in the database
--

drop table study_conference;
drop table study_project;
drop table study;

drop sequence study_id_seq;

create sequence study_id_seq start 1 increment 1;

create table study (
    study_id int not null primary key default nextval('study_id_seq'),
    name varchar(255) not null,
    create_date timestamp default now()
);
create unique index study_name_idx on study(name);

create table study_project (
    study_id int not null references study(study_id),
    master_project_id int not null references master_project(master_project_id)
);
create unique index study_project_idx on study_project(study_id, master_project_id);
create index study_project_study_id_idx on study_project(study_id);
create index study_project_master_project_id_idx on study_project(master_project_id);

create table study_conference (
    study_id int not null references study(study_id),
    conference_id int not null references conference(conference_id)
);
create unique index study_conference_idx on study_conference(study_id, conference_id);
create index study_conference_study_id_idx on study_conference(study_id);
create index study_conference_conference_id_idx on study_conference(conference_id);

insert into study(name) values ('F05-CSCW');
insert into study_project (study_id, master_project_id)
    SELECT study_id, master_project_id FROM study, master_project
     WHERE study.name='F05-CSCW'
           and master_project.master_project_name in
               ('gnome/dia', 'gnome/eog', 'gnome/evince',
                'gnome/evolution', 'gnome/f-spot', 'gnome/glade',
                'gnome/gnomemeeting', 'gnome/gnome-vfs', 'gnome/gnumeric',
                'gnome/metacity', 'gnome/nautilus', 'gnome/atk',
                'gnome/NetworkManager', 'gnome/ORBit', 'gnome/beagle',
                'gnome/gtk--', 'gnome/balsa', 'gnome/drivel', 'gnome/epiphany',
                'gnome/gconf', 'gnome/glom', 'gnome/gnomemm', 'gnome/gnome-mud',
                'gnome/gnome-network', 'gnome/gnome-pilot', 'gnome/gnome-utils',
                'gnome/gtranslator', 'gnome/memprof', 'gnome/mlview',
                'gnome/muine', 'gnome/rhythmbox', 'gnome/sawfish',
                'gnome/soup', 'gnome/gtkhtml');


insert into study_conference (study_id, conference_id)
    SELECT study_id, conference_id FROM study, conference
    WHERE study.name='F05-CSCW'
          and conference.name in
              ('Boston GNOME Summit 2004',
               'GUADEC 2000',
               'GUADEC 2001',
               'GU4DEC 2003',
               'GUADEC 2004',
               'GUADEC 2005',
               'Boston GNOME Summit 2005');

select grantall('study', 'larrym');
select grantall('study', 'mcataldo');
select grantall('study', 'pwagstro');
select grantall_seq('study_id_seq', 'larrym');
select grantall_seq('study_id_seq', 'mcataldo');
select grantall_seq('study_id_seq', 'pwagstro');

select grantall('study_project', 'larrym');
select grantall('study_project', 'mcataldo');
select grantall('study_project', 'pwagstro');

select grantall('study_conference', 'larrym');
select grantall('study_conference', 'mcataldo');
select grantall('study_conference', 'pwagstro');
