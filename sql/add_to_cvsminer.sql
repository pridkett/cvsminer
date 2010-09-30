--
-- add_to_cvsminer.sql
--

-- We should run these once and then
-- add them to the main sqlminer script

create index bug_assigned_to_idx on bug(assigned_to);
create index bug_reporter_idx on bug(reporter);
create index bug_qa_contact_idx on bug(qa_contact);
create index bug_comment_author_idx on bug_comment(comment_author);