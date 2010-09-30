--
-- bugzilla.sql
--
-- This data will probably supercede the original date from bugs.sql, but
-- for right now, I'll run them in parallel
--
-- this table is based off the original dump from GNOME Bugzilla


drop sequence bz_attachments_id_seq;
drop sequence bz_bugs_id_seq;
drop sequence bz_fielddefs_fieldid_seq;
drop sequence bz_logincookies_id_seq;
drop sequence bz_profiles_id_seq;
drop sequence bz_shadowlog_id_seq;
drop sequence bz_customfields_id_seq;
drop sequence bz_longdescs_id_seq;
drop sequence bugzilla_repo_id_seq;
drop sequence bz_milestones_id_seq;
drop sequence bz_versions_id_seq;
drop sequence bz_votes_id_seq;
drop sequence bz_op_sys_id_seq;
drop sequence bz_classifications_id_seq;
drop sequence bz_profiles_real_id_seq;
drop sequence bz_products_id_seq;
drop sequence bz_resolution_id_seq;
drop sequence bz_keyworddefs_id_seq;
drop sequence bugzilla_import_id_seq;
drop sequence bz_bugs_activity_response_id_seq;

DROP TABLE bugzilla_repos;
DROP TABLE bugzilla_import;
DROP TABLE bz_attachments;
DROP TABLE bz_attachstatusdefs;
DROP TABLE bz_attachstatuses;
DROP TABLE bz_bugs;
DROP TABLE bz_bugs_customfields;
DROP TABLE bz_cc;
DROP TABLE bz_components;
DROP TABLE bz_customfields;
DROP TABLE bz_dependencies;
DROP TABLE bz_duplicates;
DROP TABLE bz_fielddefs;
DROP TABLE bz_groups;
DROP TABLE bz_keyworddefs;
DROP TABLE bz_keywords;
DROP TABLE bz_logincookies;
DROP TABLE bz_longdescs;
DROP TABLE bz_milestones;
DROP TABLE bz_namedqueries;
DROP TABLE bz_products;
DROP TABLE bz_profiles;
DROP TABLE bz_profiles_activity;
DROP TABLE bz_shadowlog;
DROP TABLE bz_temporary_bug_assess;
DROP TABLE bz_tokens;
DROP TABLE bz_versions;
DROP TABLE bz_votes;
DROP TABLE bz_watch;
DROP TABLE bz_op_sys;
DROP TABLE bz_classifications_id_seq;
DROP TABLE bz_resolution;
DROP TABLE bz_bugs_activity_response;

create sequence bz_attachments_id_seq start 1 increment 1;
create sequence bz_customfields_id_seq start 1 increment 1;
create sequence bz_bugs_id_seq start 1 increment 1;
create sequence bz_fielddefs_fieldid_seq start 1 increment 1;
create sequence bz_logincookies_id_seq start 1 increment 1;
create sequence bz_profiles_id_seq start 1 increment 1;
create sequence bz_shadowlog_id_seq start 1 increment 1;
create sequence bugzilla_repo_id_seq start 1 increment 1;
create sequence bz_longdescs_id_seq start 1 increment 1;
create sequence bz_milestones_id_seq start 1 increment 1;
create sequence bz_versions_id_seq start 1 increment 1;
create sequence bz_votes_id_seq start 1 increment 1;
create sequence bz_op_sys_id_seq start 1 increment 1;
create sequence bz_classifications_id_seq start 1 increment 1;
create sequence bz_products_id_seq start 1 increment 1;
create sequence bugzilla_import_id_seq start 1 increment 1;
create sequence bz_resolution_id_seq start 1 increment 1;
create sequence bz_keyworddefs_id_seq start 1 increment 1;
create sequence bz_bugs_activity_response_id_seq start 1 increment 1;

-- manages storing information about repositories
create table bugzilla_repo (
  id int not null primary key default nextval('bugzilla_repo_id_seq'),
  name varchar(32) not null,
  community_id int not null references community(community_id),
  create_date timestamp not null default now());

-- used as a counter for when we're actually importing tables
create table bugzilla_import (
  id int not null primary key default nextval('bugzilla_import_id_seq'),
  name varchar(64) not null,
  bugzilla_repo_id int not null references bugzilla_repo(id),
  create_date timestamp not null default now());

CREATE TABLE bz_attachments (
  attach_id int NOT NULL primary key default nextval('bz_attachments_id_seq'),
  original_id int NOT NULL,                                                     -- the original id according to bugzilla
  bug_id int NOT NULL,
  bug_num int NOT NULL default '0',                                             -- the original bug according to bugzilla
  creation_ts timestamp NOT NULL default now(),
  description text NOT NULL,
  mimetype text NOT NULL,
  ispatch int default NULL,
  filename text NOT NULL,
  thedata bytea NOT NULL,
  submitter_id int NOT NULL default '0',
  isobsolete boolean,                                                           --
  isprivate boolean,                                                            -- eclipse
  isurl boolean,                                                                -- eclipse
  bugzilla_repo_id int not null references bugzilla_repo(id)
);
create index bz_attachment_bug_id_idx on bz_attachments(bug_id);
create index bz_attachment_creation_ts_idx on bz_attachments(creation_ts);
create index bz_attachemnt_attachment_idx on bz_attachments(ispatch);
create index bz_attachment_bug_num_idx on bz_attachments(bug_num);
create index bz_attachments_bugzilla_repo_idx on bz_attachments(bugzilla_repo_id);

--
-- Table structure for table attachstatusdefs
--

CREATE TABLE bz_attachstatusdefs (
  id int NOT NULL primary key default '0',
  name varchar(50) NOT NULL default '',
  description text,
  sortkey int NOT NULL default '0',
  product varchar(64) NOT NULL default ''
);

--
-- Table structure for table attachstatuses
--

CREATE TABLE bz_attachstatuses (
  attach_id int NOT NULL default '0',
  statusid int NOT NULL default '0',
  PRIMARY KEY  (attach_id,statusid)
);

--
-- Table structure for table bugs
--

CREATE TABLE bz_bugs (
  id int NOT NULL primary key default nextval('bz_bugs_id_seq'),  -- this is the new primary key
  original_id int NOT NULL,                                            -- the original value from the first database
  groupset bigint NOT NULL default '0',
  assigned_to int NOT NULL default '0',
  bug_file_loc text,
  bug_severity varchar(12) default NULL,
  bug_status varchar(12) default NULL,
  creation_ts timestamp default '1970-01-01 00:00:00',
  delta_ts timestamp NOT NULL default now(),
  short_desc text,
  op_sys varchar(12) default NULL,
  priority varchar(10) default NULL,
  product varchar(64) NOT NULL default '',
  op_sys_details text,
  reporter int NOT NULL default '0',
  version varchar(64) NOT NULL default '',
  component varchar(50) NOT NULL default '',
  resolution varchar(12) default NULL,
  target_milestone varchar(20) NOT NULL default '---',
  qa_contact int default NULL,
  qa_contact_id int default NULL references bz_profiles(id),
  status_whiteboard text NOT NULL,
  votes int NOT NULL default '0',
  keywords text NOT NULL,
  lastdiffed timestamp NOT NULL default '1970-01-01 00:00:00',
  everconfirmed int NOT NULL default '0',
  version_details text,
  externalcc text,
  rep_platform varchar(10) default NULL,
  reporter_accessible int NOT NULL default '1',
  cclist_accessible int NOT NULL default '1',
  bugzilla_repo_id int not null references bugzill_repo(id),
  estimated_time float,
  remaining_time float,
  alias varchar(20),
  component_id int,
  deadline timestamp
);
create index bz_bugs_assigned_to_idx on bz_bugs(assigned_to);
create index bz_bugs_creation_ts_idx on bz_bugs(creation_ts);
create index bz_bugs_delta_ts on bz_bugs(delta_ts);
create index bz_bugs_bug_severity_idx on bz_bugs(bug_severity);
create index bz_bugs_bug_status_idx on bz_bugs(bug_status);
create index bz_bugs_op_sys_idx on bz_bugs(op_sys);
create index bz_bugs_priority_idx on bz_bugs(priority);
create index bz_bugs_product_idx on bz_bugs(product);
create index bz_bugs_reporter_idx on bz_bugs(reporter);
create index bz_bugs_version_idx on bz_bugs(version);
create index bz_bugs_component_idx on bz_bugs(component);
create index bz_bugs_resolution_idx on bz_bugs(resolution);
create index bz_bugs_target_milestone_idx on bz_bugs(target_milestone);
create index bz_bugs_qa_contact_idx on bz_bugs(qa_contact);
create index bz_bugs_votes_idx on bz_bugs(votes);
create index bz_bugs_status_idx on bz_bugs(bug_status);
create index bz_bugs_bug_id_idx on bz_bugs(bug_id);
create index bz_bugs_bugzilla_repo_id_idx on bz_bugs(bugzilla_repo_id);
create index bz_bugs_original_id_idx on bz_bugs(original_id);

--
-- Table structure for table bugs_activity
--

CREATE TABLE bz_bugs_activity (
  bug_id int NOT NULL default references bz_bugs(id),
  bug_num int NOT NULL default '0', 
  who int NOT NULL default '0',
  profile_id int references bz_profiles(id),
  bug_when timestamp NOT NULL default '1970-01-01 00:00:00',
  fieldid int NOT NULL default '0',
  original_fieldid int default NULL,
  removed text,
  added text,
  attach_id int default NULL,
  original_attach_id int default NULL,
  added_id int default NULL,
  removed_id int default NULL,
);
create index bz_bugs_activity_bug_id_idx on bz_bugs_activity(bug_id);
create index bz_bugs_activity_bug_when_idx on bz_bugs_activity(bug_when);
create index bz_bugs_activity_fieldid_idx on bz_bugs_activity(fieldid);


--
-- Table structure for table bugs_customfields
--

CREATE TABLE bz_bugs_customfields (
  bug_id int NOT NULL default '0',
  cf_id int NOT NULL default '0',
  bug_num int not null default '0',
  value text
);
create index bz_bugs_customfields_bug_id_cf_id_idx on bz_bugs_customfields(bug_id, cf_id);
create index bz_bugs_customfields_cf_id_bug_id_idx on bz_bugs_customfields(cf_id, bug_id);

--
-- Table structure for table cc
--

CREATE TABLE bz_cc (
  bug_id int NOT NULL default '0',
  who int NOT NULL default '0',
  bug_num int
);
create unique index bz_cc_bug_id_idx on bz_cc(bug_id,who);
create index bz_cc_who_idx on bz_cc(who);

--
-- Table structure for table components
--

CREATE TABLE bz_components (
  id int not null default nextval('bz_components_id_seq'),
  original_id int,                                         -- if the original instance of the database had ids store it here
  value text,
  program varchar(64) default NULL,
  initialowner int default NULL,
  initialqacontact int default NULL,
  description text NOT NULL
);

--
-- Table structure for table customfields
--

CREATE TABLE bz_customfields (
  id int NOT NULL primary key default nextval('bz_customfields_id_seq'),
  name varchar(64) NOT NULL default '',
  type varchar(6) check (type in ('any','single','multi')) default NULL,
  valid_exp text NOT NULL,
  default_value text NOT NULL,
  mandatory int NOT NULL default '0',
  bugzilla_repo_id int not null references bugzilla_repo(id)
);
create index bz_customfields_name_idx on bz_customfields(name);

--
-- Table structure for table dependencies
--

CREATE TABLE bz_dependencies (
  blocked int NOT NULL default '0',
  dependson int NOT NULL default '0',
  blocked_id int not null references bz_bugs(id),
  depends_id int not null references bz_bugs(id)
);
create index bz_dependencies_blocked_idx on bz_dependencies(blocked);
create index bz_dependencies_dependson_idx on bz_dependencies(dependson);

--
-- Table structure for table duplicates
--

CREATE TABLE bz_duplicates (
  dupe_of int NOT NULL default '0',
  dupe int NOT NULL default '0',
  bug_id int not null,
  dupe_of_id int not null,
  PRIMARY KEY  (dupe)
);

--
-- Table structure for table fielddefs
--

CREATE TABLE bz_fielddefs (
  fieldid int NOT NULL primary key default nextval('bz_fielddefs_fieldid_seq'),
  original_id int not null,
  name varchar(64) NOT NULL default '',
  description text NOT NULL,
  mailhead int NOT NULL default '0',
  sortkey int NOT NULL default '0',
  bugzilla_repo_id int not null references bugzilla_repo(id),
  obsolete boolean,                                            -- eclipse
  type boolean,                                                -- eclipse
  custom boolean,                                              -- eclipse
  enter_bug boolean                                            -- eclipse
);
create unique index bz_fielddefs_name_idx on bz_fielddefs(name);
create index bz_fielddefs_sortkey_idx on bz_fielddefs(sortkey);

--
-- Table structure for table groups
--

CREATE TABLE bz_groups (
  bit bigint NOT NULL default '0',
  name varchar(255) NOT NULL default '',
  description text NOT NULL,
  isbuggroup int NOT NULL default '0',
  userregexp text NOT NULL,
  isactive int NOT NULL default '1',
  bugzilla_repo_id int not null references bugzilla_repo(id)
);
create unique index bz_groups_name_idx on bz_groups(name);
create unique index bz_groups_bit_idx on bz_groups(bit);

--
-- Table structure for table keyworddefs
--

CREATE TABLE bz_keyworddefs (
  id int NOT NULL primary key default nextval('bz_keyworddefs_id_seq'),
  name varchar(64) NOT NULL default '',
  description text,
  bugzilla_repo_id int not null references bugzilla_repo(id),
  original_id int
);
create unique index bz_keyworddefs_name_idx on bz_keyworddefs(name, bugzilla_repo_id);

--
-- Table structure for table keywords
--

CREATE TABLE bz_keywords (
  bug_id int NOT NULL default '0',
  bug_num int not null default '0',
  keywordid int NOT NULL default '0'
);
create unique index bz_keywords_bug_id_idx on bz_keywords(bug_id, keywordid);
create index bz_keywords_keywordid_idx on bz_keywords(keywordid);

--
-- Table structure for table logincookies
--

CREATE TABLE bz_logincookies (
  cookie int NOT NULL primary key default nextval('bz_logincookies_id_seq'),
  userid int NOT NULL default '0',
  lastused timestamp NOT NULL default now(),
  ipaddr varchar(40) NOT NULL default ''
);
create index bz_logincookies_lastused_idx on bz_logincookies(lastused);

--
-- Table structure for table longdescs
--

CREATE TABLE bz_longdescs (
  id int not null primary key default nextval('bz_longdescs_id_seq'),
  bug_id int NOT NULL foreign key references bz_bugs(id),             -- the system bug_id to refernce
  bug_num int not null default '0',                                   -- the origial bug_num to reference
  who int NOT NULL default '0',
  bug_when timestamp default '1970-01-01 00:00:00',
  thetext text,
  work time float default null,                                       -- eclipse
  isprivate boolean default null,                                     -- eclipse
  already_wrapped boolean default null,                               -- eclipse
  comment_id int default null,                                        -- eclipse: the original primary key from eclipse
  type int default null,                                              -- eclipse
  extra_data varchar(255) default null                                -- eclipse
);
create index bz_longdescs_bug_id_idx on bz_longdescs(bug_id);
create index bz_longdescs_bug_when_idx on bz_longdescs(bug_when);
create index bz_longdescs_who_idx on bz_longdescs(who);
-- FIXME: do we want to index like this?  If so, how in postgresql?
-- create index bz_longdescs_comment_text_idx on bz_longdescs(thetext(255));


--
-- Table structure for table milestones
--

CREATE TABLE bz_milestones (
  id int not null primary key default nextval('bz_milestones_id_seq'),
  value varchar(20) NOT NULL default '',
  product varchar(64) NOT NULL default '',
  product_id int not null references bz_products('product_id'),
  sortkey int NOT NULL default '0'
);
create unique index bz_milestones_product_idx on bz_milestones(product, value);


--
-- Table structure for table namedqueries
--

CREATE TABLE bz_namedqueries (
  userid int NOT NULL default '0',
  name varchar(64) NOT NULL default '',
  watchfordiffs int NOT NULL default '0',
  linkinfooter int NOT NULL default '0',
  query text NOT NULL
);
create unique index bz_namedqueries_userid_idx on bz_namedqueries(userid, name);
create index bz_namedqueries_watchfordiffs_idx on bz_namedqueries(watchfordiffs);


--
-- Some systems have the classifications table
CREATE TABLE bz_classifications (
  id int not null default nextval('bz_classifications_id_seq'),
  original_id int,
  name varchar(64) not null,
  description text default null,
  sortkey int not null default 0,
  bugzilla_repo_id int not null references bugzilla_repo(id)
);

--
-- Table structure for table products
--

CREATE TABLE bz_products (
  product varchar(64) default NULL,
  description text,
  milestoneurl text NOT NULL,
  disallownew int NOT NULL default '0',
  votesperuser int NOT NULL default '0',
  maxvotesperbug int NOT NULL default '10000',
  votestoconfirm int NOT NULL default '0',
  defaultmilestone varchar(20) NOT NULL default '---',
  isgnome int NOT NULL default '0',
  product_id int not null default nextval('bz_products_id_seq'),
  bugzilla_repo_id int not null references bugzilla_repo(id),
  classification_id int references classification(id),
  original_id int                                              -- stores the original ID of the product
);

--
-- Table structure for table profiles
--

CREATE TABLE bz_profiles (
  id int not null primary key default nextval('bz_profiles_real_id_seq'),  -- a database id
  userid int NOT NULL default nextval('bz_profiles_id_seq'),               -- the id from the original system
  login_name varchar(255) unique NOT NULL default '',                      -- login name of the user
  cryptpassword varchar(34) default NULL,                                  -- password
  realname varchar(255) default NULL,
  groupset bigint NOT NULL default '0',
  disabledtext text NOT NULL,
  mybugslink int NOT NULL default '1',
  blessgroupset bigint NOT NULL default '0',
  emailflags text,
  bugzilla_repo_id int not null references bugzilla_repo(id)
);

--
-- Table structure for table profiles_activity
--

-- XXX: is this multi-site safe?
CREATE TABLE bz_profiles_activity (
  userid int NOT NULL default '0',
  who int NOT NULL default '0',
  profiles_when timestamp NOT NULL default '1970-01-01 00:00:00',
  fieldid int NOT NULL default '0',
  oldvalue text,
  newvalue text
);
create index bz_profiles_activity_userid_idx on bz_profiles_activity(userid);
create index bz_profiles_activity_profiles_when_idx on bz_profiles_activity(profiles_when);
create index bz_profiles_activity_fieldid_idx on bz_profiles_activity(fieldid);


--
-- Table structure for table shadowlog
--

CREATE TABLE bz_shadowlog (
  id int NOT NULL primary key default nextval('bz_shadowlog_id_seq'),
  ts timestamp NOT NULL default now(),
  reflected int NOT NULL default '0',
  command text NOT NULL,
  bugzilla_repo_id int not null references bugzilla_repo(id)
);
create index bz_shadowlog_reflected_idx on bz_shadowlog(reflected);

--
-- Table structure for table temporary_bug_assess
--

-- XXX: is this multi-repo safe? 
CREATE TABLE bz_temporary_bug_assess (
  bug_id int default NULL,
  bug_when timestamp default NULL,
  md5_of_funcs text
);

--
-- Table structure for table tokens
--
-- XXX: I don't think I should have this
CREATE TABLE bz_tokens (
  userid int NOT NULL primary key default '0',
  issuedate timestamp NOT NULL default '1970-01-01 00:00:00',
  token varchar(16) NOT NULL default '',
  tokentype varchar(8) NOT NULL default '',
  eventdata text
);
create index bz_tokens_userid_idx on bz_tokens(userid);

--
-- Table structure for table versions
--

CREATE TABLE bz_versions (
  id int not null primary key default nextval('bz_versions_id_seq'),
  value text,
  program varchar(64) NOT NULL default '',
  product_id int not null references bz_products(product_id)
);

--
-- Table structure for table votes
--

CREATE TABLE bz_votes (
  id int not null primary key default nextval('bz_votes_id_seq'),
  who int NOT NULL default '0',
  bug_id int NOT NULL default references bz_bugs(id),
  bug_num int not null default '0',
  count int NOT NULL default '0'
);
create index bz_votes_who_idx on bz_votes(who);
create index bz_votes_bug_id_idx on bz_votes(bug_id);

--
-- Table structure for table watch
--

-- FIXME: this table may be hosed
CREATE TABLE bz_watch (
  id int not null default nextval('bz_watch_id_seq'),
  watcher int NOT NULL default '0',
  watched int NOT NULL default '0',
  bug_id integer references bz_bugs(id)
);
create unique index bz_watch_watcher_idx on bz_watch(watcher, watched);
create index bz_watch_watched_idx on bz_watch(watched);

CREATE TABLE bz_op_sys (
  id int not null default nextval('bz_op_sys_id_seq'),
  value varchar(64),
  sortkey int default 0,
  isactive int default 1,
  bugzilla_repo_id int not null references bugzilla_repo(id),
  original_id int,                                                -- original ID from first repo
);

CREATE TABLE bz_resolution (
  id int not null default nextval('bz_resolution_id_seq'),
  original_id int,
  value varchar(64),
  sortkey int default 0,
  isactive boolean,
  bugzilla_repo_id int not null references bugzilla_repo(id)
);

CREATE TABLE bz_bugs_activity_response (
  id int not null default nextval('bz_bugs_activity_response_id_seq'),
  value varchar(32) not null,
  create_date timestamp not null default now());

--select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
--select grantall_seq(relname,'mcataldo') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
--
--select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='S' and a.relowner = b.usesysid and b.usename='pwagstro';
--select grantall_seq(relname,'larrym') from pg_class a, pg_user b where a.relkind='r' and a.relowner = b.usesysid and b.usename='pwagstro' and a.relname != 'pg_%';
