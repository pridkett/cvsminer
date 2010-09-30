-- this script should go through and drop everything for a given project
-- right now I've set up that project to be eclipse
begin transaction;

-- delete from file_cvs_commit_tag where exists
--   (select file_cvs_commit_id from file_cvs_commit
--     where file_cvs_commit.file_cvs_commit_id = file_cvs_commit_tag.file_cvs_commit_id
--       and file_cvs_commit.create_date > '2008-04-01' and file_cvs_commit.create_date < '2008-04-06');
-- delete from file_cvs_commit where create_date > '2008-04-01' and create_date < '2008-04-06';
-- delete from cvs_commit where create_date > '2008-04-01' and create_date < '2008-04-06';

delete from file_cvs_commit_tag
 where exists (select file_cvs_commit.file_cvs_commit_id from file_cvs_commit, cvs_commit, project, master_project, community
                where file_cvs_commit.file_cvs_commit_id = file_cvs_commit_tag.file_cvs_commit_id and
                      cvs_commit.cvs_commit_id = file_cvs_commit.cvs_commit_id and
                      project.project_id = cvs_commit.project_id and
                      master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');

delete from tag
 where exists (select project.project_id from project, master_project, community
                where project.project_id = tag.project_id and
                      master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');


delete from file_cvs_commit
 where exists (select cvs_commit.cvs_commit_id from cvs_commit, project, master_project, community
                where cvs_commit.cvs_commit_id = file_cvs_commit.cvs_commit_id and
                      project.project_id = cvs_commit.project_id and
                      master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');

delete from file
 where exists (select project.project_id from project, master_project, community
                where project.project_id = file.project_id and
                      master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');

delete from cvs_commit
 where exists (select project.project_id from project, master_project, community
                where project.project_id = cvs_commit.project_id and
                      master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');

delete from project
 where exists (select master_project.master_project_id from master_project, community
                where master_project.master_project_id = project.master_project_id and
                      master_project.community_id = community.community_id and
                      community.community_name='eclipse');

delete from users
 where exists (select community.community_id from community
                where users.community_id = community.community_id and
                      community.community_name='eclipse');

delete from master_project
 where exists (select community.community_id from community
                where master_project.community_id = community.community_id and
                      community.community_name='eclipse');

commit;

