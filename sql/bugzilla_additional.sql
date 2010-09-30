--
-- bugzilla_additional.sql
--
-- additional tables that we've chosen to add to the bugzilla database
--

drop sequence bz_project_id_seq;
drop sequence bz_products_product_id_seq;
drop sequence bz_bugs_activity_bug_activity_id_seq;
drop sequence bz_profiles_person_id_seq;

drop table bz_product_project;
drop table bz_profiles_person;

create sequence bz_project_id_seq start 1 increment 1;
create sequence bz_products_product_id_seq start 1 increment 1;
create sequence bz_bugs_activity_bug_activity_id_seq start 1 increment 1;
create sequence bz_profiles_person_id_seq start 1 increment 1;
create sequence bz_bugs_cvs_commit_id_seq start 1 increment 1;

-- link profiles to people
create table bz_profiles_person (
    id int not null primary key default nextval('bz_profiles_person_id_seq'),
    bz_profile_id int not null references bz_profiles(userid),
    person_id int not null references person(person_id)
);

-- add in product id's
alter table bz_products add column product_id int;
alter table bz_products alter column product_id set default nextval('bz_products_id_seq');
update bz_products set product_id = nextval('bz_products_product_id_seq') where product_id is null;
alter table bz_products alter column product_id set not null;
alter table bz_products add primary key (product_id);

-- link bugzilla products to our projects
create table bz_product_project (
    product_id int references bz_products(product_id),
    project_id int references master_project(master_project_id)
);
create unique index bz_product_project_idx on bz_product_project(product_id, project_id);
create index bz_product_project_product_id_idx on bz_product_project(product_id);
create index bz_product_project_project_id_idx on bz_product_project(project_id);
alter table bz_product_project add column id int;
create sequence bz_product_project_id_seq start 1 increment 1;
alter table bz_product_project alter column id set default nextval('bz_product_project_id_seq');
update bz_product_project set id=nextval('bz_product_project_id_seq');
alter table bz_product_project alter column id set not null;
alter table bz_product_project add primary key(id);

      
-- add an index to bz_products for faster searching
create unique index bz_products_product_idx on bz_products(product);

-- link bugzilla bugs to bugzilla products
alter table bz_bugs add column product_id int;
update bz_bugs set product_id = bz_products.product_id from bz_products where bz_products.product = bz_bugs.product;
alter table bz_bugs alter column product_id set not null;
alter table bz_bugs add foreign key (product_id) references bz_products(product_id);
create index bz_bugs_product_id_idx on bz_bugs(product_id);

-- update the bz_bugs_activity table
alter table bz_bugs_activity add column bug_activity_id int;
update bz_bugs_activity set bug_activity_id = nextval('bz_bugs_activity_bug_activity_id_seq');
alter table bz_bugs_activity alter column bug_activity_id set not null;
alter table bz_bugs_activity add primary key(bug_activity_id);
alter table bz_bugs_activity add foreign key(bug_id) references bz_bugs(bug_id);
alter table bz_bugs_activity alter column bug_activity_id set default nextval('bz_bugs_activity_bug_activity_id_seq');

create table bz_bugs_cvs_commit (
    id int not null default nextval('bz_bugs_cvs_commit_id_seq'),
    bug_id int not null references bz_bugs(id),
    cvs_commit_id int not null references cvs_commit(cvs_commit_id)
);

select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';

select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';

