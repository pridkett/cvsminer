--
-- maillists.sql
--
-- additional tables needed to store information about the mailing lists
--
-- basically three tables:
-- mailing_lists - contains information on the mailing lists
-- mail_message - a message sent to the mailing list
-- mail_message_to - a list of recipients for the message
-- mail_file_archive - represents what archive we loaded each message from
--

drop table mail_message_reference;
drop table mail_message_to;
drop table mail_message cascade;
drop table mail_file_archive;
drop table mailing_list cascade;

drop sequence mail_message_reference_id_seq;
drop sequence mailing_list_id_seq;
drop sequence mail_message_id_seq;
drop sequence mail_message_to_id_seq;
drop sequence mail_file_archive_id_seq;

create sequence mail_message_reference_id_seq start 1 increment 1;
create sequence mailing_list_id_seq start 1 increment 1;
create sequence mail_message_id_seq start 1 increment 1;
create sequence mail_message_to_id_seq start 1 increment 1;
create sequence mail_file_archive_id_seq;

create table mailing_list (
	mailing_list_id int not null primary key default nextval('mailing_list_id_seq'),
	name varchar(255) NOT NULL,
    project_id int references master_project(master_project_id),
    create_date timestamp not null default now()
);
create index mailing_list_product_idx on mailing_list(project_id);
create index mailing_list_name_idx on mailing_list(name);

create table mail_file_archive (
    mail_file_archive_id int not null primary key default nextval('mail_file_archive_id_seq'),
    mailing_list_id int not null references mailing_list(mailing_list_id),
    filename varchar(255) NOT NULL,
    start_date timestamp not null,
    stop_date timestamp not null,
    create_date timestamp not null default now()
);

create table mail_message (
	mail_message_id int not null primary key default nextval('mail_message_id_seq'),
	mailing_list_id int NOT NULL references mailing_list(mailing_list_id),
    mail_file_archive_id int not null references mail_file_archive(mail_file_archive_id),
    from_name varchar(255),
	email varchar(255) NOT NULL,
    email_address_id int,
	subject varchar(255) NOT NULL,
	body text,
	message_date timestamp,
    message_id varchar(255) NOT NULL default '##UNKNOWN##',
    message_parent int references mail_message(mail_message_id),
    in_reply_to varchar(255)
);
create index mail_message_mailing_list_id_idx on mail_message(mailing_list_id);
create index mail_message_message_date_idx on mail_message(message_date);
create index mail_message_message_id_idx on mail_message(message_id);
create index mail_message_message_parent_idx on mail_message(message_parent);
create index mail_message_archive_id_idx on mail_message(mail_file_archive_id);
alter table mail_message add constraint email_address_id_fk FOREIGN KEY (email_address_id) references email_address(email_address_id);
update mail_message set email_address_id=s.email_address_id from email_address s where s.email=mail_message.email;
create index mail_message_email_address_id_idx on mail_message(email_address_id);
-- this partial index is VERY helpful when searching for messages that need to be reparented
create index mail_message_null_parent_idx on mail_message(in_reply_to) where message_parent is null;


create table mail_message_to (
    mail_message_to_id int not null primary key default nextval('mail_message_to_id_seq'),
	mail_message_id int references mail_message(mail_message_id),
    message_to boolean NOT NULL default 'f',
    to_name varchar(255) not null,
	email varchar(255) NOT NULL,
    email_address_id int
);
alter table mail_message_to add constraint mail_message_to_email_address_id_fk FOREIGN KEY (email_address_id) references email_address(email_address_id);
create index mail_message_to_id_idx on mail_message_to(mail_message_id);
create index mail_message_to_email_idx on mail_message_to(email);
update mail_message_to set email_address_id=s.email_address_id from email_address s where s.email=mail_message_to.email;
create index mail_message_to_email_address_id_idx on mail_message_to(email_address_id);

create table mail_message_reference (
    mail_message_reference_id int not null primary key default nextval('mail_message_reference_id_seq'),
    mail_message_id int not null references mail_message(mail_message_id),
    reference varchar(255) not null
);
create index mail_message_reference_mail_message_id_idx on mail_message_reference(mail_message_id);

