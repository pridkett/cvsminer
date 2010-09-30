--
-- person.sql
--

\connect cvsminer

drop index corporation_name_idx;
drop index person_corporation_person_idx;
drop index alias_name_idx;
drop index alias_person_idx;
drop index person_primary_alias_idx;
drop index email_address_idx;
drop index corporation_domain_idx;

drop table corporation_domain;
drop table person_corporation;
drop table corporation;
drop table person_user;
drop table email_address;
drop table alias cascade;
drop table person cascade;
drop table record_source;

drop sequence record_source_id_seq;
drop sequence corporation_id_seq;
drop sequence person_corporation_person_id_seq;

create sequence record_source_id_seq start 1 increment 1;
create sequence corporation_id_seq start 1 increment 1;
create sequence person_corporation_id_seq start 1 increment 1;
create sequence corporation_domain_id_seq start 1 increment 1;

create table record_source (
    record_source_id int not null primary key default nextval('record_source_id_seq'),
    child_name varchar(255),
    create_date timestamp not null default now(),
    who varchar(255) not null,
    tool varchar(255) not null,
    tool_timestamp timestamp not null default now(),
    source1 varchar(255),
    source1_id int,
    source2 varchar(255),
    source2_id int,
    notes varchar(255)
);

create table person (
    person_id int not null primary key default nextval('record_source_id_seq')
);

create sequence alias_id_seq start 1 increment 1;
create table alias (
    alias_id int not null primary key default nextval('alias_id_seq'),
    name varchar(255) not null,
    person_id int references person(person_id)
);

alter table person add column primary_alias int references alias(alias_id);
alter table person alter column primary_alias set not null;
alter table person add column needs_work boolean;

create table person_user (
    person_user_id int not null primary key default nextval('record_source_id_seq'),
    person_id int not null references person(person_id),
    user_id int not null references users(user_id)
);
create index person_user_user_id_idx on person_user (user_id);
create index person_user_person_id_idx on person_user (person_id);


create table email_address (
    email_address_id int not null primary key default nextval('record_source_id_seq'),
    email varchar(255) not null unique,
    person_id int references person(person_id)
);

create table corporation (
    corporation_id int not null primary key default nextval('corporation_id_seq'),
    name varchar(255) not null unique,
    homepage varchar(255),
    icon varchar(255),
    prop_distributor bool default null,
    prop_manufacturer bool default null,
    create_date timestamp not null default now(),
    modify_date timestamp not null default now()
);

create table person_corporation (
    person_corporation_id int not null primary key default nextval('person_corporation_id_seq'),
    person_id int not null references person(person_id),
    corporation_id int not null references corporation(corporation_id),
    start_date timestamp,
    stop_date timestamp,
    create_date timestamp not null default now(),
    modify_date timestamp not null default now()
);
create sequence person_corporation_project_id_seq start 1 increment 1;
create table user_corporation_project (
    id int not null primary key default nextval('person_corporation_project_id_seq'),
    user_id int not null references users(user_id),
    corporation_id int not null references corporation(corporation_id),
    project_id int not null references master_project(master_project_id),
    year int not null,
    month int not null,
    date timestamp not null,
    num_commits int not null,
    lines_added int not null,   
    lines_removed int default null,
    lines_delta int default null,
    create_date timestamp not null default now()
);

create table corporation_domain (
    corporation_domain_id int not null primary key default nextval('corporation_domain_id_seq'),
    corporation_id int not null references corporation(corporation_id),
    domain varchar(255) not null unique,
    create_date timestamp not null default now(),
    modify_date timestamp not null default now()
);

create index person_corporation_person_idx on person_corporation(person_id);
create index corporation_name_idx on corporation(name);
create index email_address_idx on email_address(email);
create index alias_name_idx on alias(name);
create index alias_person_idx on alias(person_id);
create index person_primary_alias_idx on person(primary_alias);

select 'GRANTING TABLE RIGHTS';
select grantall('record_source', 'mcataldo');
select grantall('record_source', 'pwagstro');
select grantall('person', 'mcataldo');
select grantall('person', 'pwagstro');
select grantall('alias', 'mcataldo');
select grantall('alias', 'pwagstro');
select grantall('person_user', 'mcataldo');
select grantall('person_user', 'pwagstro');
select grantall('email_address', 'mcataldo');
select grantall('email_address', 'pwagstro');
select grantall('corporation', 'mcataldo');
select grantall('corporation', 'pwagstro');
select grantall('person_corporation', 'mcataldo');
select grantall('person_corporation', 'pwagstro');

select 'GRANTING SEQUENCE RIGHTS';
select grantall_seq('record_source_id_seq', 'larrym');
select grantall_seq('record_source_id_seq', 'mcataldo');
select grantall_seq('record_source_id_seq', 'pwagstro');
select grantall_seq('corporation_id_seq', 'pwagstro');
select grantall_seq('corporation_id_seq', 'mcataldo');
select grantall_seq('person_corporation_id_seq', 'pwagstro');
select grantall_seq('person_corporation_id_seq', 'mcataldo');

-- fill up the corporation table with some default values
insert into corporation (name, homepage) values ('RedHat', 'http://www.redhat.com/');
insert into corporation (name, homepage) values ('Novell', 'http://www.novell.com/');
insert into corporation (name, homepage) values ('Sun Microsystems', 'http://www.sun.com/');
insert into corporation (name, homepage) values ('Ximian', 'http://www.ximian.com/');
insert into corporation (name, homepage) values ('Nokia', 'http://www.nokia.com/');
insert into corporation (name, homepage) values ('Opened Hand', 'http://www.o-hand.com/');
insert into corporation (name, homepage) values ('Xandros', 'http://www.xandros.com/');
insert into corporation (name, homepage) values ('Fluendo', 'http://www.fluendo.com/');
insert into corporation (name, homepage) values ('Mandriva', 'http://www.mandriva.com/');
insert into corporation (name, homepage) values ('Conectiva', 'http://www.conectiva.com/');
insert into corporation (name, homepage) values ('VA Software', 'http://www.vasoftware.com/');
insert into corporation (name, homepage) values ('Imendio', 'http://www.imendio.com/');
insert into corporation (name, homepage) values ('Helixcode', 'http://www.helixcode.com/');
insert into corporation (name, homepage) values ('Code Factory', 'http://www.codefactory.se/');
insert into corporation (name, homepage) values ('SuSE', 'http://www.suse.com/');
insert into corporation (name, homepage) values ('Wipro', 'http://www.wipro.com/');
insert into corporation (name, homepage) values ('Eazel', 'http://www.eazel.com/');
insert into corporation (name, homepage) values ('Canonical', 'http://www.canonical.com/');

-- add in a new domain for a corporation
CREATE OR REPLACE FUNCTION add_corporation_domain (text,text) RETURNS integer AS '
  DECLARE
    
    -- Declare aliases for user input.
    corporation_name ALIAS FOR $1;
    domain_name ALIAS FOR $2;
    
    -- Declare a variable to hold the customer ID number.
    cid INTEGER;
  
  BEGIN
    -- get the corporation id for the corporation of interest
    SELECT INTO cid corporation_id FROM corporation
      WHERE lower(name) = corporation_name;
    
    INSERT INTO corporation_domain(corporation_id, domain) VALUES (cid, domain_name);

    -- Return the ID number.
    RETURN cid;
  END;
' LANGUAGE 'plpgsql';
select add_corporation_domain('redhat','redhat.com');
select add_corporation_domain('helixcode', 'helixcode.com');
select add_corporation_domain('ximian', 'ximian.com');
select add_corporation_domain('va software', 'vasoftware.com');
select add_corporation_doamin('va software', 'valinux.com');
select add_corporation_domain('va software', 'varesearch.com');
select add_corporation_domain('imendio', 'imendio.com');
select add_corporation_domain('conectiva', 'conectiva.com');
select add_corporation_domain('conectiva', 'conectiva.com.br');
select add_corporation_domain('novell', 'novell.com');
select add_corporation_domain('sun microsystems', 'sun.com');
select add_corporation_domain('nokia', 'nokia.com');
select add_corporation_domain('opened hand', 'o-hand.com');
select add_corporation_domain('xandros', 'xandros.com');
select add_corporation_domain('fluendo', 'fluendo.com');
select add_corporation_domain('code factory', 'codefactory.se');
select add_corporation_domain('suse', 'suse.com');
select add_corporation_domain('suse', 'suse.cz');
select add_corporation_domain('suse', 'suse.de');
select add_corporation_domain('wipro', 'wipro.com');
select add_corporation_domain('eazel', 'eazel.com');
select add_corporation_domain('mandriva', 'mandrakesoft.com');
select add_corporation_domain('mandriva', 'mandriva.com');
select add_corporation_domain('canonical', 'canonical.com');
