/*
SAS for analysis of clustering data
*/

OPTIONS NOCENTER linesize=125 pagesize=70;

TITLE;


/* ************************
   LOAD AND CREATE DATASETS
   ************************
*/
DATA neighborhood;
    /* INFILE '/home/pwagstro/code/cvsminer/data/clustering/neighborhood.csv' delimiter=',' DSD TRUNCOVER LRECL=1000; */
    INFILE '/home/pwagstro/code/cvsminer/src/network/guess/clustering/neighborhood-8week-0overlap.csv' delimiter=',' DSD TRUNCOVER LRECL=1000;
    INPUT PROJECTID WEEKID CLUSTERID COMMERCIALCOMMITS             /* 1-4 */
        VOLUNTEERCOMMITS ACTIVEFILES COMMERCIALUSERS               /* 5-7 */
        VOLUNTEERUSERS COMMERCIALFILES VOLUNTEERFILES              /* 8-10 */
        CROSSCLUSTERCOMMITS COMMERCIALCROSSCLUSTERCOMMITS          /* 11-12 */
        VOLUNTEERCROSSCLUSTERCOMMITS TOTALPERIODCOMMITS            /* 13-14 */
        TOTALPERIODFILES COMMERCIALCROSSCLUSTERUSERS               /* 15-16 */
        VOLUNTEERCROSSCLUSTERUSERS                                 /* 17 */
        DISTRIBUTORCOMMITS DISTRIBUTORUSERS                        /* 18-19 */
        MANUFACTURERCOMMITS MANUFACTURERUSERS                      /* 20-21 */
        NEWCOMMERCIALUSERS NEWVOLUNTEERUSERS                       /* 22-23 */
        NEWPROJECTCOMMERCIALUSERS NEWPROJECTVOLUNTEERUSERS         /* 24-25 */
        NEWPROJECTDISTRIBUTORUSERS NEWPROJECTMANUFACTURERUSERS     /* 26-27 */
        PROJECTVOLUNTEERUSERS PROJECTCOMMERCIALUSERS               /* 28-29 */
        PROJECTDISTRIBUTORUSERS PROJECTMANUFACTURERUSERS           /* 30-31 */
        CONTINUINGVOLUNTEERUSERS CONTINUINGCOMMERCIALUSERS         /* 32-33 */
        CONTINUINGDISTRIBUTORUSERS CONTINUINGMANUFACTURERUSERS      /* 33-34 */
        REDHATU NOVELLU SUNU XIMIANU NOKIAU                        /* 35-39 */
        OPENEDHANDU XANDROSU FLUENDOU MANDRIVAU CONECTIVAU
        VASOFTWAREU IMENDIOU HELIXCODEU CODEFACTORYU SUSEU
        WIPROU EAZELU CANONICALU
        REDHATC NOVELLC SUNC XIMIANC NOKIAC
        OPENEDHANDC XANDROSC FLUENDOC MANDRIVAC CONECTIVAC
        VASOFTWAREC IMENDIOC HELIXCODEC CODEFACTORYC SUSEC
        WIPROC EAZELC CANONICALC
        avgBugFixed avgBugzillaProjects
        avgMailNewThreads avgMailProjects
        avgExtraMailProjects avgCvsCommits
        avgCvsProjects
        pAvgMailMessages pAvgMailNewThreads pAvgCvsCommits pAvgBugFixed
        periodBugsFixed periodBugsProjects periodBugComments periodDevBugComments
        periodMailNewthreads periodMailLists periodMailMessages periodDevMailMessages
        periodCVSCommits periodCVSProjects
        
        LCLUSTERID LCOMMERCIALCOMMITS
        LVOLUNTEERCOMMITS LACTIVEFILES LCOMMERCIALUSERS
        LVOLUNTEERUSERS LCOMMERCIALFILES LVOLUNTEERFILES
        LCROSSCLUSTERCOMMITS LCOMMERCIALCROSSCLUSTERCOMMITS
        LVOLUNTEERCROSSCLUSTERCOMMITS LTOTALPERIODCOMMITS
        LTOTALPERIODFILES LCOMMERCIALCROSSCLUSTERUSERS
        LVOLUNTEERCROSSCLUSTERUSERS
        LDISTRIBUTORCOMMITS LDISTRIBUTORUSERS
        LMANUFACTURERCOMMITS LMANUFACTURERUSERS
        LNEWCOMMERCIALUSERS LNEWVOLUNTEERUSERS
        LNEWPROJECTCOMMERCIALUSERS LNEWPROJECTVOLUNTEERUSERS
        LNEWPROJECTDISTRIBUTORUSERS LNEWPROJECTMANUFACTURERUSERS
        LPROJECTVOLUNTEERUSERS LPROJECTCOMMERCIALUSERS
        LPROJECTDISTRIBUTORUSERS LPROJECTMANUFACTURERUSERS
        LCONTINUINGVOLUNTEERUSERS LCONTINUINGCOMMERCIALUSERS
        LCONTINUINGDISTRIBUTORUSERS LCONTINUINGMANUFACTURERUSERS
        
        LREDHATU LNOVELLU LSUNU LXIMIANU LNOKIAU
        LOPENEDHANDU LXANDROSU LFLUENDOU LMANDRIVAU LCONECTIVAU
        LVASOFTWAREU LIMENDIOU LHELIXCODEU LCODEFACTORYU LSUSEU
        LWIPROU LEAZELU LCANONICALU
        LREDHATC LNOVELLC LSUNC LXIMIANC LNOKIAC
        LOPENEDHANDC LXANDROSC LFLUENDOC LMANDRIVAC LCONECTIVAC
        LVASOFTWAREC LIMENDIOC LHELIXCODEC LCODEFACTORYC LSUSEC
        LWIPROC LEAZELC LCANONICALC
        lavgBugFixed lavgBugzillaProjects
        lavgMailNewThreads lavgMailProjects
        lavgExtraMailProjects lavgCvsCommits
        lavgCvsProjects
        lpAvgMailMessages lpAvgMailNewThreads lpAvgCvsCommits lpAvgBugFixed    
        lPeriodBugsFixed lPeriodBugsProjects lPeriodBugComments lPeriodDevBugComments
        lPeriodMailNewthreads lPeriodMailLists lPeriodMailMessages lPeriodDevMailMessages
        lPeriodCVSCommits lPeriodCVSProjects
        ;

    OLDVOLUNTEERUSERS = VOLUNTEERUSERS - NEWVOLUNTEERUSERS;

    LOGVOLUNTEERUSERS = LOG2(VOLUNTEERUSERS+1);
    LOGCOMMERCIALUSERS = LOG2(COMMERCIALUSERS+1);
    LOGMANUFACTURERUSERS = LOG2(MANUFACTURERUSERS+1);
    LOGDISTRIBUTORUSERS = LOG2(DISTRIBUTORUSERS+1);
    LOGNEWVOLUNTEERUSERS = LOG2(NEWVOLUNTEERUSERS+1);
    LOGOLDVOLUNTEERUSERS = LOG2(OLDVOLUNTEERUSERS+1);
    
    ** create a few more useful variables;
    TOTALCOMMITS = COMMERCIALCOMMITS + VOLUNTEERCOMMITS;
    FRACVOLUNTEERCOMMITS = VOLUNTEERCOMMITS/MAX(1,COMMERCIALCOMMITS+VOLUNTEERCOMMITS);
    FRACCOMMERCIALCOMMITS = COMMERCIALCOMMITS/MAX(1,COMMERCIALCOMMITS+VOLUNTEERCOMMITS);
    FRACCROSSCLUSTERCOMMITS = CROSSCLUSTERCOMMITS/MAX(1,COMMERCIALCOMMITS+VOLUNTEERCOMMITS);
    FRACVOLUNTEERUSERS = VOLUNTEERUSERS/MAX(1,VOLUNTEERUSERS+COMMERCIALUSERS);
    FRACCOMMERCIALUSERS = COMMERCIALUSERS/MAX(1,VOLUNTEERUSERS+COMMERCIALUSERS);
    USERS = VOLUNTEERUSERS + COMMERCIALUSERS;
    COMMITS = VOLUNTEERCOMMITS + COMMERCIALCOMMITS;
    CROSSCLUSTERUSERS = COMMERCIALCROSSCLUSTERUSERS + VOLUNTEERCROSSCLUSTERUSERS;
    FRACTOTALCOMMITS = COMMITS / MAX(1,TOTALPERIODCOMMITS);    
    LOGACTIVEFILES = LOG2(ACTIVEFILES+1);
    LOGCOMMITS = LOG2(COMMITS+1);
    PROJECTSIZE = LOG2((ACTIVEFILES + COMMITS)/2 + 1);
    
    ** create a few more useful variables;
    LTOTALCOMMITS = LCOMMERCIALCOMMITS + LVOLUNTEERCOMMITS;
    LFRACVOLUNTEERCOMMITS = LVOLUNTEERCOMMITS/MAX(1,LCOMMERCIALCOMMITS+LVOLUNTEERCOMMITS);
    LFRACCOMMERCIALCOMMITS = LCOMMERCIALCOMMITS/MAX(1,LCOMMERCIALCOMMITS+LVOLUNTEERCOMMITS);
    LFRACCROSSCLUSTERCOMMITS = LCROSSCLUSTERCOMMITS/MAX(1,LCOMMERCIALCOMMITS+LVOLUNTEERCOMMITS);
    LUSERS = LVOLUNTEERUSERS + LCOMMERCIALUSERS;
    LCOMMITS = LVOLUNTEERCOMMITS + LCOMMERCIALCOMMITS;
    LCROSSCLUSTERUSERS = LCOMMERCIALCROSSCLUSTERUSERS + LVOLUNTEERCROSSCLUSTERUSERS;
    LFRACTOTALCOMMITS = LCOMMITS / MAX(1,LTOTALPERIODCOMMITS);    
    LFRACVOLUNTEERUSERS = LVOLUNTEERUSERS/MAX(1,LVOLUNTEERUSERS+LCOMMERCIALUSERS);
    LFRACCOMMERCIALUSERS = LCOMMERCIALUSERS/MAX(1,LVOLUNTEERUSERS+LCOMMERCIALUSERS);
    LLOGACTIVEFILES = LOG(LACTIVEFILES+1);
    LLOGCOMMITS = LOG2(LCOMMITS+1);
    LPROJECTSIZE = LOG2((ACTIVEFILES + COMMITS)/2 + 1);
    
    LLOGVOLUNTEERUSERS = LOG2(LVOLUNTEERUSERS+1);
    LLOGCOMMERCIALUSERS = LOG2(LCOMMERCIALUSERS+1);
    LLOGMANUFACTURERUSERS = LOG2(LMANUFACTURERUSERS+1);
    LLOGDISTRIBUTORUSERS = LOG2(LDISTRIBUTORUSERS+1);
    
    PROJCLUSTER = PROJECTID * 100 + CLUSTERID;

    ** calculate how many volunteers were lost;
    LOSTVOLUNTEERUSERS = LVOLUNTEERUSERS - CONTINUINGVOLUNTEERUSERS;
    LOSTCOMMERCIALUSERS = LCOMMERCIALUSERS - CONTINUINGCOMMERCIALUSERS;
    LOSTMANUFACTURERUSERS = LMANUFACTURERUSERS - CONTINUINGMANUFACTURERUSERS;
    LOSTDISTRIBUTORUSERS = LDISTRIBUTORUSERS - CONTINUINGDISTRIBUTORUSERS;

    ** a general delta stat;
    VOLUNTEERDELTA = VOLUNTEERUSERS - LVOLUNTEERUSERS;
RUN;


** *****************************************************************************;
** add in the additional fonts;
** *****************************************************************************;
proc fontreg mode=all;
    fontpath '/usr/share/matplotlib/';
run;

** proc registry list startat='core\printing\freetype\fonts';
** run;

DATA NOCLUSTER;
    SET NEIGHBORHOOD;
    IF CLUSTERID ^= 0 THEN DELETE;
RUN;

DATA ALLCLUSTER;
    SET NEIGHBORHOOD;
    IF CLUSTERID = 0 THEN DELETE;
RUN;

proc sort data=allcluster;
    by projcluster;
run;

** *****************************************************************************;
** attempt to fit a curve to the various data elements.  also, spit out a graph;
** showing the distribution and the curves on it;
** *****************************************************************************;

** plot the distribution of volunteer users;
** goptions reset=all device=sasprtc; **;
** options printerpath=(pdf PDFFILE) orientation=LANDSCAPE PAPERSIZE=LETTER; **;
** symbol width=6; **;

** filename PDFFILE "volunteerDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Volunteer Histogram"; **;
**     var volunteerusers; **;
**     histogram / **;
**         midpoints=0 to 20 by 2 **;
**         cfill=yellow **;
**         /* normal (color=green) */ **;
**         lognormal (theta=-1 color=red) **;
**         /* weibull (theta=est color=orange) **;
**         gamma (theta=est color=blue) */ **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** *\* plot the log distribution of volunteers; **;
** filename PDFFILE "logVolunteerDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Volunteer Histogram"; **;
**     var logvolunteerusers; **;
**     histogram / **;
**         cfill=yellow **;
**         normal (color=green) **;
**         lognormal (theta=-1 color=red) **;
**         /* weibull (theta=est color=orange) **;
**         gamma (theta=est color=blue) */ **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** *\* plot the distribution of commercial users; **;
** filename PDFFILE "commercialDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Commercial Histogram"; **;
**     var commercialusers; **;
**     histogram / **;
**         midpoints=0 to 20 by 2 **;
**         cfill=yellow **;
**         /* normal (color=green) */ **;
**         lognormal (theta=-1 color=red) **;
**         /* weibull (theta=est color=orange) **;
**         gamma (theta=est color=blue) */ **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** *\* plot the distribution of new volunteer users; **;
** filename PDFFILE "newVolunteerDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** title "New Volunteer Histogram"; **;
** proc capability data=nocluster; **;
**     var newvolunteerusers; **;
**     histogram / **;
**         midpoints=0 to 20 by 1 **;
**         cfill=yellow **;
**         normal (color=green) **;
**         lognormal (theta=-1 color=red) **;
**         /* weibull (theta=est color=orange) */ **;
**         gamma (theta=est color=blue) **;
**         exponential (color=orange) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** *\* plot the distribution of old volunteer users; **;
** filename PDFFILE "oldVolunteerDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Old Volunteer Histogram"; **;
**     var oldvolunteerusers; **;
**     histogram / **;
**         midpoints=-1 to 20 by 1 **;
**         cfill=yellow **;
**         normal (color=green) **;
**         lognormal (theta=-1 color=red) **;
**         weibull (theta=est color=orange) **;
**         gamma (theta=est color=blue) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** *\* plot the distribution of volunteer changes; **;
** filename PDFFILE "volunteerDeltaDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Volunteer Delta Histogram"; **;
**     var volunteerdelta; **;
**     histogram / **;
**         midpoints=-10 to 10 by 1 **;
**         cfill=yellow **;
**         normal (color=green) **;
**         lognormal (theta=est color=red) **;
**         weibull (theta=est color=orange) **;
**         gamma (theta=est color=blue) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** filename PDFFILE "logCommitsDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Commits"; **;
**     var logcommits; **;
**     histogram / **;
**         cfill=yellow **;
**         normal (color=green) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** filename PDFFILE "projectSizeDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "Project Size"; **;
**     var projectsize; **;
**     histogram / **;
**         cfill=yellow **;
**         normal (color=green) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** filename PDFFILE "commitsSizeDistribution.pdf"; **;
** legend1 frame cframe=ligr cborder=black position=center; **;
** proc capability data=nocluster; **;
**     title "log(commits)"; **;
**     var logcommits; **;
**     histogram / **;
**         cfill=yellow **;
**         normal (color=green) **;
**         nospeclegend **;
**         vaxis = axis1 **;
**         cframe = ligr; **;
**     inset n mean(5.3) median(5.3) std='Std Dev'(5.3) skewness(5.3) **;
**         / pos = ne header='Summary Statistics' cfill=blank font="Bitstream Vera Sans"; **;
**     axis1 label=(a=90 r=0); **;
** run; **;

** get some generic statistics about the entire data set;
proc univariate data=nocluster;
    title "Descriptive Statistics of Data";
    var volunteerusers commercialusers activefiles commits distributorusers manufacturerusers newvolunteerusers;
RUN;

proc univariate data=nocluster;
    title "Descriptive Statistics of Mediating Variables";
    var         lPeriodBugsProjects lPeriodMailMessages lPeriodDevMailMessages lPeriodCVSProjects;
RUN;

proc sort data=nocluster;
    by projectid;
run;

data new;
    set nocluster;
    by projectid;
    if first.projectid then count=0;
    count+1;
    if last.projectid then output;
run;

proc univariate data=new;
    title "Descriptive stats of number of obs per project";
    var count;
RUN;

PROC CORR DATA=NOCLUSTER;
    VAR VOLUNTEERUSERS LVOLUNTEERUSERS LCOMMERCIALUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LCOMMITS;
    TITLE "Correlations of predictor variables (normal)"
RUN;

PROC CORR DATA=NOCLUSTER;
    VAR LOGVOLUNTEERUSERS LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS;
    TITLE "Correlations of predictor variables (logged)"
RUN;
       

** *****************************************************************************;
** time to redo all the regressions with lots of stuff ;
** *****************************************************************************;
******************;
** HYPOTHESIS 1 **;
******************;
PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 1 Model1: Commercial Developers Lower the Number of Volunteers Working on Modules (Ignoring Clustering)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw;
RUN;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    CLASS PROJCLUSTER;
    TITLE 'Hypothesis 1 Model2: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Module)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr;
RUN;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    CLASS PROJCLUSTER PROJECTID;
    TITLE 'Hypothesis 1 Model3: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Project/Module)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID;
    RANDOM INTERCEPT /subject=PROJCLUSTER(PROJECTID);
RUN;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     CLASS PROJCLUSTER; **;
**     TITLE 'Hypothesis 1.2b: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Module)'; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS **;
**         lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsProjects **;
**         lpAvgMailMessages lpAvgMailNewThreads lpAvgCvsCommits lpAvgBugFixed/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER; **;
** RUN; **;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 1 Model4: Commercial Developers Lower the Number of Volunteers Working on Modules (Ignoring Clustering)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw;
RUN;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    CLASS PROJCLUSTER;
    TITLE 'Hypothesis 1 Model5: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Module)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJCLUSTER;
RUN;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     CLASS PROJCLUSTER; **;
**     TITLE 'Hypothesis 1.2bb: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Module)'; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS **;
**         lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsProjects **;
**         lpAvgMailMessages lpAvgMailNewThreads lpAvgCvsCommits lpAvgBugFixed/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER; **;
** RUN; **;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    CLASS PROJCLUSTER PROJECTID;
    TITLE 'Hypothesis 1 Model6: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Module)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID;
    RANDOM INTERCEPT /subject=PROJCLUSTER(PROJECTID);
RUN;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     CLASS PROJECTID; **;
**     TITLE 'Hypothesis 1.3: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Project)'; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;


** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     CLASS PROJCLUSTER PROJECTID; **;
**     TITLE 'Hypothesis 1.5: Commercial Developers Lower the Number of Volunteers Working on Modules (Clustered by Project/Module)'; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGDISTRIBUTORUSERS LLOGMANUFACTURERUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER(PROJECTID); **;
** RUN; **;
    
** PROC CORR DATA=ALLCLUSTER; **;
**     TITLE "Correlations for Log Hypothesis 1"; **;
**     VAR LOGVOLUNTEERUSERS LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LPROJECTSIZE; **;
** RUN; **;

** *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*; **;
** *\* HYPOTHESIS 2 *\*; **;
** *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*; **;
** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 2: Commercial Developers Attract Volunteers to Projects'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGNEWVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 2a: Commercial Developers Attract Volunteers to Projects (By commercial class)'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGNEWVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

** *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*; **;
** *\* HYPOTHESIS 3 *\*; **;
** *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*; **;
** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 3: Commercial Developers Attract Volunteers to Projects'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGOLDVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 3a: Commercial Developers Attract Volunteers to Projects (By commercial class)'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGOLDVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

** *\* Examine the delta of users *\*; **;
** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Volunteer Delta'; **;
**     CLASS PROJECTID; **;
**     MODEL  VOLUNTEERDELTA = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGACTIVEFILES LLOGCOMMITS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

********************;
** New Hypotheses **;
********************;
PROC REG DATA=NOCLUSTER;
    TITLE 'Testing for Multicollinearity in the data';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/vif tol collin;
RUN;

PROC REG DATA=NOCLUSTER;
    TITLE 'Testing for Multicollinearity in the data (split)';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGDISTRIBUTORUSERS LLOGMANUFACTURERUSERS LLOGCOMMITS/vif tol collin;
RUN;

PROC REG DATA=NOCLUSTER;
    TITLE 'Testing for multicollinearity in the mediated data';
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
        lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsProjects
        lavgCvsCommits/vif tol collin;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 2: Commercial Developers Increase all Volunteer Participation';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 2/float: Commercial Developers Increase all Volunteer Participation';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGCOMMERCIALUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT LLOGVOLUNTEERUSERS/subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4: Commercial Developers Attract Volunteers to Projects (By commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/delta: Commercial Developers Attract Volunteers to Projects (By commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT LLOGVOLUNTEERUSERS/subject=PROJECTID type=un gcorr;
RUN;

** note, in this equation, I removed lavgCvsCommits because it has very high correlation *;
** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 3/4/Control: Commercial Developers Attract Volunteers to Projects (Byo commercial class)'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS **;
**         lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsProjects **;
**         lpAvgMailMessages lpAvgMailNewThreads lpAvgCvsCommits lpAvgBugFixed/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;


** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 3/4/Mediating: Commercial Developers Attract Volunteers to Projects (Byo commercial class)'; **;
**     CLASS PROJECTID; **;
**     MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS **;
**         lPeriodBugsFixed lPeriodBugsProjects lPeriodMailNewthreads lPeriodMailLists **;
**         lPeriodCVSCommits lPeriodCVSProjects/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

PROC CORR DATA=NOCLUSTER;
    VAR LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
            lPeriodMailMessages lPeriodDevMailMessages lPeriodBugsProjects lPeriodCVSProjects;
    TITLE "Correlations of Mediating Variables"
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
          lPeriodDevMailMessages lPeriodBugsProjects lPeriodCVSProjects/s ddfm=bw;
**         lPeriodBugsFixed lPeriodBugsProjects lPeriodBugComments lPeriodDevBugComments lPeriodMailNewthreads lPeriodMailLists **;
**         lPeriodMailMessages lPeriodDevMailMessages lPeriodCVSCommits lPeriodCVSProjects/s ddfm=bw; **;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating-1: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
        lPeriodBugsFixed/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating-2: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
        lPeriodBugsProjects/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating-3: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
          lPeriodMailNewthreads/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating-4: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
          lPeriodMailLists/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating-5: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
          lPeriodCVSCommits/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3/4/Mediating: Commercial Developers Attract Volunteers to Projects (Byo commercial class)';
    CLASS PROJECTID;
    MODEL LOGVOLUNTEERUSERS = LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS
          lPeriodCVSProjects/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

** PROC CORR DATA=NOCLUSTER; **;
**     VAR LOGVOLUNTEERUSERS LLOGVOLUNTEERUSERS LLOGMANUFACTURERUSERS LLOGDISTRIBUTORUSERS LLOGCOMMITS **;
**         lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsCommits **;
**         lavgCvsProjects  lpAvgMailMessages lpAvgMailNewThreads lpAvgCvsCommits lpAvgBugFixed; **;
**     TITLE "Correlations of Control Predictor Variables" **;
** RUN; **;
PROC CORR DATA=NOCLUSTER;
    VAR lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsCommits
        lavgCvsProjects;
    TITLE "Correlations of Control Predictor Variables"
RUN;

proc univariate data=nocluster;
    title "Descriptive Statistics of Control Predictor Variables";
    VAR lavgBugFixed lavgBugzillaProjects lavgMailNewThreads lavgMailProjects lavgExtraMailProjects lavgCvsCommits
        lavgCvsProjects;
RUN;

** *****************************************************************************;
** Hypothesis 1: The Presence of Commercial Developers will Drive Volunteer Users Away;
** This is primariliy the modularity argument;
** *****************************************************************************;
** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 1: Commercial Developers Drive volunteers to other modules'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 1a: Commercial Developers Drive volunteers to other modules'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 1: Commercial Developers Drive volunteers to other modules (continuing)'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 1: Commercial Developers Drive volunteers to other modules (continuing)'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES LTOTALCOMMITS LUSERS LLOGACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'Hypothesis 1a: Commercial Developers Drive volunteers to other modules (continuing)'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** *****************************************************************************;
** Hypothesis 2: The publicity around commercial developers participating in a project
** will result in an increase in new developers participating in the project;
** *****************************************************************************;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 2: Commercial Developers Attract Volunteers to Projects';
    CLASS PROJECTID;
    MODEL NEWVOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 2a: Commercial Developers Attract Volunteers to Projects (By commercial class)';
    CLASS PROJECTID;
    MODEL NEWVOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

** *****************************************************************************;
** Hypothesis 3: The work habits of commercial developers will drive volunteers away
** from projects to other projects
** *****************************************************************************;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3: Commercial developers lower number of continuing volunteers';
    CLASS PROJECTID;
    MODEL OLDVOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3a: Commercial developers lower number of continuing volunteers (by commercial class)';
    CLASS PROJECTID;
    MODEL OLDVOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3a: Commercial developers lower number of all volunteers (by commercial class)';
    CLASS PROJECTID;
    MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

** ***************************************************************************;
** the impact on continuing number of individuals ;
** ***************************************************************************;
PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Commercial Users Impact on Continuing Volunteer Developers';
    CLASS PROJECTID;
    MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Commercial Users Impact on Continuing Volunteer Developers (by class)';
    CLASS PROJECTID;
    MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Commercial Users Impact on Continuing Volunteer Developers (with previous stability)';
    CLASS PROJECTID;
    MODEL CONTINUINGVOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS LCONTINUINGVOLUNTEERUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Commercial Users Impact on Lost Volunteer Developers';
    CLASS PROJECTID;
    MODEL LOSTVOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

** *****************************************************************************;
** exploration of other ideas;
** *****************************************************************************;

** does the activity of that period have an impact on the number of commits;
PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 1b: Commercial Developers Drive volunteers to other modules';
    CLASS PROJCLUSTER;
    MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LTOTALCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 2b: Commercial Developers Attract Volunteers to Projects (By commercial class)';
    CLASS PROJECTID;
    MODEL NEWVOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LTOTALPERIODCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 3b: Commercial developers lower number of continuing volunteers (by commercial class)';
    CLASS PROJECTID;
    MODEL OLDVOLUNTEERUSERS = LVOLUNTEERUSERS LDISTRIBUTORUSERS LMANUFACTURERUSERS LTOTALPERIODCOMMITS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC MIXED DATA=NOCLUSTER noclprint COVTEST;
    TITLE 'What is role of volunteer users on the number of commits';
    CLASS PROJECTID;
    MODEL TOTALPERIODCOMMITS = VOLUNTEERUSERS MANUFACTURERUSERS DISTRIBUTORUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJECTID type=un gcorr;
RUN;

PROC CORR DATA=NOCLUSTER;
VAR TOTALPERIODCOMMITS VOLUNTEERUSERS MANUFACTURERUSERS DISTRIBUTORUSERS;
RUN;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL OLD-M1: Volunteer Users MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL NEW-M1-SIMPLE: New Volunteer Users MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL NEWVOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL NEW-M1: New Volunteer Users MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL NEWVOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LNEWVOLUNTEERUSERS LNEWPROJECTVOLUNTEERUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC CORR DATA=ALLCLUSTER; **;
**     TITLE 'MODEL NEW-M1-CORR: Correlations for NEW-M1'; **;
**     VAR NEWVOLUNTEERUSERS LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LNEWVOLUNTEERUSERS LNEWPROJECTVOLUNTEERUSERS LACTIVEFILES; **;
** RUN; **;

** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL NEW-PM1-SIMPLE: New Volunteer Users MLM based on users'; **;
**     CLASS PROJECTID; **;
**     MODEL NEWPROJECTVOLUNTEERUSERS = LPROJECTVOLUNTEERUSERS LPROJECTMANUFACTURERUSERS LPROJECTDISTRIBUTORUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=NOCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL NEW-PM1: New Volunteer Users MLM based on users'; **;
**     CLASS PROJECTID; **;
**     MODEL NEWPROJECTVOLUNTEERUSERS = LPROJECTVOLUNTEERUSERS LPROJECTMANUFACTURERUSERS LPROJECTDISTRIBUTORUSERS LNEWPROJECTVOLUNTEERUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJECTID type=un gcorr; **;
** RUN; **;
    
** /* **;
**  * SIMPLE LINEAR REGRESSIONS **;
**  */ **;

** /* **;
**  * this tries to explain the variance based only on the number of users and the activity. **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES LTOTALPERIODFILES; **;
**     Adj R-Sq: 0.4238 **;
**                       Intercept             1       -0.00366        0.06653      -0.05      0.9562 **;
**                       LVOLUNTEERUSERS       1        0.48715        0.03919      12.43      <.0001 **;
**                       LCOMMERCIALUSERS      1        0.02457        0.01100       2.23      0.0259 **;
**                       LACTIVEFILES          1        0.00157     0.00071730       2.19      0.0292 **;
**                       LTOTALPERIODFILES     1     0.00006710     0.00003802       1.76      0.0782 **;
**    With that in minde, remove LTOTALPERIODFILES. **;
**  */ **;
** PROC CORR DATA=ALLCLUSTER; **;
**     TITLE 'Testing A-R1 Predictors'; **;
**     VAR VOLUNTEERUSERS LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES LMANUFACTURERUSERS LDISTRIBUTORUSERS; **;
** RUN; **;

** PROC REG DATA=ALLCLUSTER; **;
**     TITLE 'A-R1: Simple Regression Based on Users'; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LACTIVEFILES LMANUFACTURERUSERS LDISTRIBUTORUSERS; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC REG DATA=ALLCLUSTER; **;
**     TITLE 'A-R1-COMM: Simple Regression Based on Users'; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LACTIVEFILES LCOMMERCIALUSERS; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC REG DATA=ALLCLUSTER; **;
**     TITLE 'A-R1-LOG: Simple Regression Based on Users'; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LLOGACTIVEFILES LMANUFACTURERUSERS LDISTRIBUTORUSERS; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC REG DATA=ALLCLUSTER; **;
**     TITLE 'A-R1s: Simple Regression Based on Users'; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** /* check the related correlations here **;
**  * I'm still very concerned about how high some of these values are **;
**  */ **;

** PROC CORR DATA=ALLCLUSTER OUTP=CLUSTERR1; **;
**     TITLE 'A-R1: Correlations'; **;
**     VAR VOLUNTEERUSERS LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES; **;
** RUN; **;
                                   
** /* **;
**  * *\*\*\*\*\*\*\*\*\*\*\* **;
**  * MIXED MODELS **;
**  * *\*\*\*\*\*\*\*\*\*\*\* **;
**  */ **;
** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1: MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1-COMM: MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1-LOG: MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LLOGACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1b: MLM based on users (no active files)'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1c: MLM based on users (no commercial differentiation)'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=ALLCLUSTER noclprint COVTEST; **;
**     TITLE 'MODEL A-M1d: MLM based on users'; **;
**     CLASS PROJCLUSTER; **;
**     MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS LACTIVEFILES/s ddfm=bw; **;
**     RANDOM INTERCEPT LMANUFACTURERUSERS/subject=PROJCLUSTER type=un gcorr; **;
** RUN; **;

** /* **;
**  * *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* **;
**  * PCA To Get Better Data **;
**  * *\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\* **;
**  */ **;

** DATA ACLUSTERCORRIN; **;
**     SET ALLCLUSTER; **;
**     IF LCLUSTERID=. THEN DELETE; **;
** RUN; **;

** /* the following variables have no variance: **;
**     nokiau, openedhandu, xandrosu, fluendou, conectivau, vasoftwareu, canonicalu **;
**  */ **;
** PROC FACTOR data=ACLUSTERCORRIN method=principal priors=one mineigen=0.95 reorder score **;
**       rotate=varimax fuzz=0.2 flag=0.4 OUT=CLUSTERFACTOR NFACTORS=10; * scree preplot plot;  **;
**       TITLE 'ACLUSTER: PCA with varimax rotation (and output data set)'; **;
**       VAR LCOMMERCIALCOMMITS **;
**           LVOLUNTEERCOMMITS LACTIVEFILES LCOMMERCIALUSERS **;
**           LVOLUNTEERUSERS LCOMMERCIALFILES LVOLUNTEERFILES **;
**           LCROSSCLUSTERCOMMITS LCOMMERCIALCROSSCLUSTERCOMMITS **;
**           LVOLUNTEERCROSSCLUSTERCOMMITS LTOTALPERIODCOMMITS **;
**           LTOTALPERIODFILES LCOMMERCIALCROSSCLUSTERUSERS **;
**           LVOLUNTEERCROSSCLUSTERUSERS **;
**           LREDHATU LNOVELLU LSUNU LXIMIANU **;
**           LMANDRIVAU LIMENDIOU LHELIXCODEU LCODEFACTORYU LSUSEU **;
**           LWIPROU LEAZELU **;
**           LREDHATC LNOVELLC LSUNC LXIMIANC **;
**           LMANDRIVAC LIMENDIOC LHELIXCODEC LCODEFACTORYC LSUSEC **;
**           LWIPROC LEAZELC; **;
** RUN; **;

** PROC PRINT DATA=CLUSTERFACTOR; **;
** RUN; **;

** /* **;
**  * now we repeat the analysis using the factors **;
**  * no need to do correlations because they, by definition, have 0 **;
**  */ **;

** PROC REG DATA=CLUSTERFACTOR; **;
**     TITLE 'R3: Simple Regression Of Users Based on Factors'; **;
**     MODEL VOLUNTEERUSERS = factor1-factor10; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC REG DATA=CLUSTERFACTOR; **;
**     TITLE 'R4: Simple Regression Of Commits Based on Factors'; **;
**     MODEL VOLUNTEERCOMMITS = factor1-factor10; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** /* **;
**  * now some MLMs **;
**  */ **;
** PROC MIXED DATA=CLUSTERFACTOR noclprint COVTEST; **;
**     TITLE 'MODEL M3: MLM based on users'; **;
**     CLASS CLUSTERID; **;
**     MODEL VOLUNTEERUSERS = factor1-factor10/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=CLUSTERID type=un gcorr; **;
** RUN; **;

** PROC MIXED DATA=CLUSTERFACTOR noclprint COVTEST; **;
**     TITLE 'MODEL M4: MLM based on commits'; **;
**     CLASS CLUSTERID; **;
**     MODEL VOLUNTEERCOMMITS = factor1-factor10/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=CLUSTERID type=un gcorr; **;
** RUN; **;
    



** /* **;
**  * How abot we try some simpler PCA **;
**  */ **;
** PROC FACTOR data=ACLUSTERCORRIN method=principal priors=one mineigen=0.95 reorder score **;
**       rotate=varimax fuzz=0.2 flag=0.4 OUT=CLUSTERFACTORUSERS NFACTORS=5; * scree preplot plot;  **;
**       TITLE 'ACLUSTER: PCA with varimax rotation (and output data set -- Users Only)'; **;
**     VAR LCOMMERCIALUSERS LVOLUNTEERUSERS **;
**         LCOMMERCIALFILES LVOLUNTEERFILES **;
**         LTOTALPERIODFILES LCOMMERCIALCROSSCLUSTERUSERS **;
**         LVOLUNTEERCROSSCLUSTERUSERS **;
**         LREDHATU LNOVELLU LSUNU LXIMIANU **;
**         LMANDRIVAU LIMENDIOU LHELIXCODEU LCODEFACTORYU LSUSEU **;
**         LWIPROU LEAZELU; **;
** RUN; **;

** PROC FACTOR data=ACLUSTERCORRIN method=principal priors=one mineigen=0.95 reorder score **;
**       rotate=varimax fuzz=0.2 flag=0.4 OUT=CLUSTERFACTORUSERS NFACTORS=5; * scree preplot plot;  **;
**       TITLE 'ACLUSTER-2: PCA with varimax rotation (and output data set -- Users Only)'; **;
**     VAR LCOMMERCIALUSERS LVOLUNTEERUSERS **;
**         LCOMMERCIALFILES LVOLUNTEERFILES **;
**         LTOTALPERIODFILES LCOMMERCIALCROSSCLUSTERUSERS **;
**         LVOLUNTEERCROSSCLUSTERUSERS **;
**         LREDHATU LNOVELLU LSUNU LXIMIANU **;
**         LMANDRIVAU LIMENDIOU LHELIXCODEU LCODEFACTORYU LSUSEU **;
**         LWIPROU LEAZELU LMANUFACTURERUSERS LDISTRIBUTORUSERS; **;
** RUN; **;

** PROC REG DATA=CLUSTERFACTORUSERS; **;
**     TITLE 'R3c: Simple Regression Of Users Based on Factors (simple factors)'; **;
**     MODEL VOLUNTEERUSERS = factor1-factor4; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC MIXED DATA=CLUSTERFACTORUSERS noclprint COVTEST; **;
**     TITLE 'MODEL M3c: MLM based on users (simple factors)'; **;
**     CLASS CLUSTERID; **;
**     MODEL VOLUNTEERUSERS = factor1-factor4/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=CLUSTERID type=un gcorr; **;
** RUN; **;

** PROC FACTOR data=ACLUSTERCORRIN method=principal priors=one mineigen=0.95 reorder score **;
**       rotate=varimax fuzz=0.2 flag=0.4 OUT=CLUSTERFACTORCOMMITS NFACTORS=4; * scree preplot plot;  **;
**       TITLE 'CLUSTER: PCA with varimax rotation (and output data set -- Commits Only)'; **;
**     VAR LCOMMERCIALCOMMITS **;
**         LVOLUNTEERCOMMITS LACTIVEFILES **;
**         LCOMMERCIALFILES LVOLUNTEERFILES **;
**         LCROSSCLUSTERCOMMITS LCOMMERCIALCROSSCLUSTERCOMMITS **;
**         LVOLUNTEERCROSSCLUSTERCOMMITS LTOTALPERIODCOMMITS **;
**         LTOTALPERIODFILES **;
**         LREDHATC LNOVELLC LSUNC LXIMIANC **;
**         LMANDRIVAC LIMENDIOC LHELIXCODEC LCODEFACTORYC LSUSEC **;
**         LWIPROC LEAZELC; **;
** RUN; **;

** PROC REG DATA=CLUSTERFACTORCOMMITS; **;
**     TITLE 'R4c: Simple Regression Of Commits Based on Factors'; **;
**     MODEL VOLUNTEERCOMMITS = factor1-factor4; **;
**     OUTPUT out=resids residual=rscore predicted=pscore student=student rstudent=rstudent cookd=cookd; **;
** RUN; **;

** PROC MIXED DATA=CLUSTERFACTORCOMMITS noclprint COVTEST; **;
**     TITLE 'MODEL M4c: MLM based on commits on Factors'; **;
**     CLASS CLUSTERID; **;
**     MODEL VOLUNTEERCOMMITS = factor1-factor4/s ddfm=bw; **;
**     RANDOM INTERCEPT /subject=CLUSTERID type=un gcorr; **;
** RUN; **;

