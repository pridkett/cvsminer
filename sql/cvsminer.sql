--
-- cvsminer.sql
--

-- In order to reload this script you MUST comment out this first line.  This
-- is here as an anti-shoot-yourself-in-the-foot measure
\q

\connect cvsminer
-- make sure the language is added
\! createlang plpython cvsminer

drop table file_cvs_commit_tag cascade;
drop table tag cascade;
drop table file_cvs_commit cascade;
drop table cvs_commit cascade;
drop table cvs_state cascade;
drop table file cascade;
drop table file_class_regex cascade;
drop table file_class cascade;
drop table project_user cascade;
drop table users cascade;
drop table release cascade;
drop table project cascade;
drop table master_project cascade;
drop table community cascade;

drop sequence community_id_seq;
drop sequence cvs_state_id_seq;
drop sequence user_id_seq;
drop sequence cvs_commit_id_seq;
drop sequence file_id_seq;
drop sequence project_id_seq;
drop sequence file_cvs_commit_id_seq;
drop sequence file_class_id_seq;
drop sequence file_class_regex_id_seq;
drop sequence tag_id_seq;
drop sequence release_id_seq;

create sequence community_id_seq start 1 increment 1;
create sequence master_project_id_seq start 1 increment 1;
create sequence project_id_seq start 1 increment 1;
create sequence file_id_seq start 1 increment 1;
create sequence cvs_commit_id_seq start 1 increment 1;
create sequence user_id_seq start 1 increment 1;
create sequence cvs_state_id_seq start 1 increment 1;
create sequence file_cvs_commit_id_seq start 1 increment 1;
create sequence file_class_id_seq start 1 increment 1;
create sequence file_class_regex_id_seq start 1 increment 1;
create sequence tag_id_seq start 1 increment 1;
create sequence release_id_seq start 1 increment 1;

create table community (
    community_id int not null primary key default nextval('community_id_seq'),
    community_name varchar(255),
    create_date timestamp not null default now()
);

create table master_project (
    master_project_id int not null primary key default nextval('master_project_id_seq'),
    master_project_name varchar(255),
    community_id int not null references community(community_id),
    create_date timestamp not null default now()
);
create index master_project_community_idx on master_project(community_id);

create table project (
    project_id int not null
        primary key default nextval('project_id_seq'),o
    master_project_id int not null references master_project(master_project_id),
    project_name varchar(64),
    project_path varchar(255),
    create_date timestamp not null default now(),
    modify_date timestamp not null default now()
);
create index project_name_idx on project(project_name);
create index project_master_project_idx on project(master_project_id);

--
-- I know this violates the singular naming scheme, it's just that user is
-- is a reserved keyword in SQL
--
create table users (
    user_id int not null
        primary key default nextval('user_id_seq'),
    user_name varchar(64),
    community_id int not null references community(community_id),
    create_date timestamp not null default now()
);

create table project_user (
    project_id int not null references project(project_id),
    user_id int not null references users(user_id)
);

create table file (
    file_id int not null
        primary key default nextval('file_id_seq'),
    project_id int not null references project(project_id),
    file_name varchar(1024),
    create_date timestamp not null default now()
);
create index file_project_idx on file(project_id);

create table cvs_state (
    cvs_state_id int not null
        primary key default nextval('cvs_state_id_seq'),
    cvs_state_name varchar(255),
    create_date timestamp not null default now()
);

create table cvs_commit (
    cvs_commit_id int not null
        primary key default nextval('cvs_commit_id_seq'),
    project_id int not null references project(project_id),
    user_id int not null references users(user_id),
    start_date timestamp not null,
    stop_date timestamp not null,
    message_intro varchar(255) not null,
    branch varchar(255) default null,
    message text not null,
    create_date timestamp not null default now()
);

create index cvs_commit_project_idx on cvs_commit(project_id);
create index cvs_commit_project_user_idx on cvs_commit(project_id, user_id);
create index cvs_commit_project_user_message_idx on cvs_commit(project_id, user_id, message_intro);
create index cvs_commit_start_date_idx on cvs_commit(start_date);

create index cvs_commit_user_idx on cvs_commit(user_id);

create table file_cvs_commit (
    file_cvs_commit_id int not null
        primary key default nextval('file_cvs_commit_id_seq'),
    file_id int not null references file(file_id),
    cvs_commit_id int not null references cvs_commit(cvs_commit_id),
    date timestamp not null,
    revision varchar(32) not null,
    cvs_state_id int not null references cvs_state(cvs_state_id),
    lines_added int,
    lines_removed int,
    create_date timestamp not null default now()
);
create index file_cvs_commit_file_idx on file_cvs_commit(file_id);
create index file_cvs_commit_cvs_commit_idx on file_cvs_commit(cvs_commit_id);
create index file_cvs_commit_revision_idx on file_cvs_commit(file_id, revision);

create table tag (
    tag_id int not null primary key default nextval('tag_id_seq'),
    project_id int not null references project(project_id),
    name varchar(255) not null,
    create_date timestamp not null default now()
);
create index tag_name_idx on tag(name);
create index tag_project_id_idx on tag(project_id);

create table file_cvs_commit_tag (
    file_cvs_commit_id int not null references file_cvs_commit(file_cvs_commit_id),
    tag_id int not null references tag(tag_id)
);
create index file_cvs_commit_tag_commit_idx on file_cvs_commit_tag(file_cvs_commit_id);
create index file_cvs_commit_tag_tag_idx on file_cvs_commit_tag(tag_id);

create table file_class (
    file_class_id int not null
        primary key default nextval('file_class_id_seq'),
    file_class_desc varchar(255) not null,
    parent_file_class_id int references file_class(file_class_id),
    create_date timestamp not null default now()
);
create index file_class_file_desc_idx on file_class(file_class_desc);
alter table file add column file_class_id int references file_class(file_class_id);

-- add in a new domain for a corporation
CREATE OR REPLACE FUNCTION add_file_class_parent (text,text) RETURNS integer AS '
  DECLARE
    
    -- Declare aliases for user input.
    class_name ALIAS FOR $1;
    parent_name ALIAS FOR $2;
    
    -- Declare a variable to hold the customer ID number.
    cid INTEGER;
  
  BEGIN
    -- get the corporation id for the corporation of interest
    SELECT INTO cid file_class_id FROM file_class
      WHERE lower(file_class_desc) = lower(parent_name);
    
    INSERT INTO file_class(file_class_desc, parent_file_class_id) VALUES (class_name, cid);

    -- Return the ID number.
    RETURN cid;
  END;
' LANGUAGE 'plpgsql';

insert into file_class(file_class_desc) values ('Source Code');
insert into file_class(file_class_desc) values ('Documentation');
insert into file_class(file_class_desc) values ('Graphics');
insert into file_class(file_class_desc) values ('Compilation Helpers');
insert into file_class(file_class_desc) values ('Translation Files');
insert into file_class(file_class_desc) values ('UNKNOWN');
insert into file_class(file_class_desc) values ('Support Files');
insert into file_class(file_class_desc) values ('User Interface');
insert into file_class(file_class_desc) values ('Sound');

select add_file_class_parent('C Source Code', 'source code');
select add_file_class_parent('C Source Code Headers', 'c source code');
select add_file_class_parent('C++ Source Code', 'source code');
select add_file_class_parent('C++ Source Code Headers', 'c++ source code');
select add_file_class_parent('Perl Source Code', 'source code');
select add_file_class_parent('Python Source Code', 'source code');
select add_file_class_parent('C# Source Code', 'source code');
select add_file_class_parent('Java Source Code', 'source code');
select add_file_class_parent('Scheme Source Code', 'source code');
select add_file_class_parent('Corba IDL Files', 'source code');
select add_file_class_parent('TCL Source Code', 'source code');
select add_file_class_parent('PNG Graphics', 'graphics');
select add_file_class_parent('JPG Graphics', 'graphics');
select add_file_class_parent('SVG Graphics', 'graphics');
select add_file_class_parent('GIF Graphics', 'graphics');
select add_file_class_parent('XPM Graphics', 'graphics');
select add_file_class_parent('XCF Graphics', 'graphics');
select add_file_class_parent('PO Translation Files', 'translation files');
select add_file_class_parent('ChangeLogs', 'documentation');
select add_file_class_parent('README Files', 'documentation');
select add_file_class_parent('HTML Files', 'documentation');
select add_file_class_parent('XML Files', 'documentation');
select add_file_class_parent('SGML Files', 'documentation');
select add_file_class_parent('TXT Files', 'documentation');
select add_file_class_parent('XSLT Files', 'documentation');
select add_file_class_parent('Autoconf Files', 'compilation helpers');
select add_file_class_parent('Automake Files', 'compilation helpers');
select add_file_class_parent('Autogen Files', 'compilation helpers');
select add_file_class_parent('Pkg-Config Files', 'compilation helpers');
select add_file_class_parent('RPM Spec Files', 'compilation helpers');
select add_file_class_parent('M4 Macro Files', 'compilation helpers');
select add_file_class_parent('Shell Scripts', 'compiilation helpers');
select add_file_class_parent('GNOME .desktop Files', 'Support Files');
select add_file_class_parent('intltool files', 'translation files');
select add_file_class_parent('CVS Control Files', 'Support Files');
select add_file_class_parent('WAV Sound Files', 'Sound');
select add_file_class_parent('OGG Sound Files', 'Sound');

create table file_class_regex (
    file_class_regex_id int not null
        primary key default nextval('file_class_regex_id_seq'),
    file_class_regex varchar(255) not null,
    file_class_id int not null references file_class(file_class_id),
    create_date timestamp not null default now()
);

CREATE OR REPLACE FUNCTION regex_insert (text,text) RETURNS integer AS '
  DECLARE
    
    -- Declare aliases for user input.
    regex_text ALIAS FOR $1;
    class_name ALIAS FOR $2;
    
    -- Declare a variable to hold the customer ID number.
    cid INTEGER;
  
  BEGIN
    -- get the corporation id for the corporation of interest
    SELECT INTO cid file_class_id FROM file_class
      WHERE lower(file_class_desc) = lower(class_name);
    
    INSERT INTO file_class_regex(file_class_regex, file_class_id) VALUES (regex_text, cid);

    -- Return the ID number.
    RETURN cid;
  END;
' LANGUAGE 'plpgsql';

select regex_insert('\\.c$', 'C source code');
select regex_insert('\\.h$', 'C source code headers');
select regex_insert('\\.cpp$', 'C++ source code');
select regex_insert('\\.cxx$', 'C++ source code');
select regex_insert('\\.cc$', 'C++ source code');
select regex_insert('\\.hpp$', 'C++ source code headers');
select regex_insert('\\.hh$', 'C++ source code headers');
select regex_insert('\\.hxx$', 'C++ source code headers');
select regex_insert('\\.[pP][lL]$', 'Perl source code');
select regex_insert('\\.[pP][mM]$', 'Perl source code');
select regex_insert('\\.py$', 'Python source code');
select regex_insert('\\.cs$', 'C# source code');
select regex_insert('\\.java$', 'Java source code');
select regex_insert('\\.scm$', 'Scheme source code');
select regex_insert('\\.tcl$', 'TCL source code');
select regex_insert('\\.[pP][nN][gG]$', 'PNG graphics');
select regex_insert('\\.[jJ][pP][eE]?[gG]$', 'JPG graphics');
select regex_insert('\\.[sS][vV][gG]$', 'SVG graphics');
select regex_insert('\\.[gG][iI][fF]$', 'GIF graphics');
select regex_insert('\\.[xX][pP][mM]$', 'XPM graphics');
select regex_insert('\\.xcf$', 'XCF graphics');
select regex_insert('\\.po$', 'PO Translation Files');
select regex_insert('\\.gmo$', 'Translation files');
select regex_insert('^POTFILES', 'Translation Files');
select regex_insert('^ChangeLog', 'Changelogs');
select regex_insert('^README', 'README Files');
select regex_insert('\\.s?html?$', 'HTML files');
select regex_insert('\\.wml$', 'HTML files');
select regex_insert('(\\.xml(\\.in)?)$', 'XML files');
select regex_insert('^configure\\.in$', 'autoconf files');
select regex_insert('Makefile\\.am$', 'automake files');
select regex_insert('^autogen\\.sh$', 'autogen files');
select regex_insert('(\\.pc(\\.in)?)$', 'pkg-config files');
select regex_insert('(\\.spec(\\.in)*)$', 'rpm spec files');
select regex_insert('\\.m4$', 'm4 macro files');
select regex_insert('^intltool', 'intltool files');
select regex_insert('^AUTHORS', 'Documentation');
select regex_insert('^MAINTAINERS', 'Documentation');
select regex_insert('^HACKING', 'Documentation');
select regex_insert('^INSTALL', 'Documentation');
select regex_insert('^MAINTAINERS', 'Documentation');
select regex_insert('^NEWS', 'Documentation');
select regex_insert('^TODO', 'Documentation');
select regex_insert('^COPYING', 'Documentation');
select regex_insert('\\.idl$', 'Corba IDL Files');
select regex_insert('\\.cvsignore$', 'CVS Control Files');
select regex_insert('\\.sgml$', 'SGML Files');
select regex_insert('\\.txt$', 'TXT Files');
select regex_insert('Makefile$', 'compilation helpers');
select regex_insert('\\.glade$', 'user interface');
select regex_insert('\\.ogg$', 'ogg sound files');
select regex_insert('\\.wav$', 'wav sound files');
select regex_insert('\\.sh$', 'shell scripts');
select regex_insert('\\.xslt?$', 'xslt files');

------------------------------------------------------------------------
-- various variables related to software releases and community releases
------------------------------------------------------------------------

create table release (
    release_id int not null primary key default nextval('release_id_seq'),
    community_id int references community(community_id),
    master_project_id int references master_project(master_project_id),
    project_id int references project(project_id),
    release_version varchar(32) not null,
    developer_release bool default False,
    major_release bool default False,
    bugfix_release bool default False,  
    release_date timestamp not null,
    release_announcer_id int references person(person_id),
    create_date timestamp not null
);
