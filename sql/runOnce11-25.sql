--
-- run once 11-25.sql
--

-- I updated the database to seperate the names from
-- the person table by creating an alias table.
-- this table structure is already included in the
-- person.sql script.  It is included to allow you
-- to upgrade to the new structure and not lose any of
-- your existing data (conferences).

drop sequence person_id_seq;
drop sequence person_user_id_seq;
drop sequence email_address_id_seq;

drop index alias_name_idx;
drop index alias_person_idx;
drop index person_primary_alias_idx;

drop table alias cascade;

create table alias (
    alias_id int not null primary key default nextval('record_source_id_seq'),
    name varchar(255),
    person_id int references person(person_id)
);

-- Adds records to alias table using name and person_id
insert into alias (person_id, name) select * from person;

alter table person
  add column "primary_alias" int;

update person set primary_alias = alias.alias_id from alias where alias.person_id = person.person_id;

alter table person drop name;

alter table person
  alter column "person_id" set default nextval('record_source_id_seq')

alter table person_user
  alter column "person_user_id" set default nextval('record_source_id_seq')

alter table email_address
  alter column "email_address_id" set default nextval('record_source_id_seq')

alter table email_address alter column person_id drop not null;

create index alias_name_idx on alias(name);
create index alias_person_idx on alias(person_id);
create index person_primary_alias_idx on person(primary_alias);

select grantall('alias', 'larrym');
select grantall('alias', 'mcataldo');
select grantall('alias', 'pwagstro');

