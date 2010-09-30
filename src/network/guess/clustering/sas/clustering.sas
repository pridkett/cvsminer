/*
SAS for analysis of clustering data
*/

OPTIONS linesize=120 pagesize=70;

TITLE;


/* ************************
   LOAD AND CREATE DATASETS
   ************************
*/
DATA neighborhood;
    INFILE '/home/pwagstro/code/cvsminer/data/clustering/neighborhood.csv' delimiter=',' DSD TRUNCOVER LRECL=1000;
    INPUT PROJECTID WEEKID CLUSTERID COMMERCIALCOMMITS
        VOLUNTEERCOMMITS ACTIVEFILES COMMERCIALUSERS
        VOLUNTEERUSERS COMMERCIALFILES VOLUNTEERFILES
        CROSSCLUSTERCOMMITS COMMERCIALCROSSCLUSTERCOMMITS
        VOLUNTEERCROSSCLUSTERCOMMITS TOTALPERIODCOMMITS
        TOTALPERIODFILES COMMERCIALCROSSCLUSTERUSERS
        VOLUNTEERCROSSCLUSTERUSERS
        DISTRIBUTORCOMMITS DISTRIBUTORUSERS
        MANUFACTURERCOMMITS MANUFACTURERUSERS
        NEWCOMMERCIALUSERS NEWVOLUNTEERUSERS
        NEWPROJECTCOMMERCIALUSERS NEWPROJECTVOLUNTEERUSERS
        NEWPROJECTDISTRIBUTORUSERS NEWPROJECTMANUFACTURERUSERS
        PROJECTVOLUNTEERUSERS PROJECTCOMMERCIALUSERS
        PROJECTDISTRIBUTORUSERS PROJECTMANUFACTURERUSERS
        REDHATU NOVELLU SUNU XIMIANU NOKIAU
        OPENEDHANDU XANDROSU FLUENDOU MANDRIVAU CONECTIVAU
        VASOFTWAREU IMENDIOU HELIXCODEU CODEFACTORYU SUSEU
        WIPROU EAZELU CANONICALU
        REDHATC NOVELLC SUNC XIMIANC NOKIAC
        OPENEDHANDC XANDROSC FLUENDOC MANDRIVAC CONECTIVAC
        VASOFTWAREC IMENDIOC HELIXCODEC CODEFACTORYC SUSEC
        WIPROC EAZELC CANONICALC
        
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
        
        LREDHATU LNOVELLU LSUNU LXIMIANU LNOKIAU
        LOPENEDHANDU LXANDROSU LFLUENDOU LMANDRIVAU LCONECTIVAU
        LVASOFTWAREU LIMENDIOU LHELIXCODEU LCODEFACTORYU LSUSEU
        LWIPROU LEAZELU LCANONICALU
        LREDHATC LNOVELLC LSUNC LXIMIANC LNOKIAC
        LOPENEDHANDC LXANDROSC LFLUENDOC LMANDRIVAC LCONECTIVAC
        LVASOFTWAREC LIMENDIOC LHELIXCODEC LCODEFACTORYC LSUSEC
        LWIPROC LEAZELC LCANONICALC;

    OLDVOLUNTEERUSERS = VOLUNTEERUSERS - NEWVOLUNTEERUSERS;
    
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
    LOGACTIVEFILES = LOG(MAX(ACTIVEFILES,1));
    
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
    LLOGACTIVEFILES = LOG(MAX(LACTIVEFILES,1));
    
    PROJCLUSTER = PROJECTID * 100 + CLUSTERID;
RUN;

DATA NOCLUSTER;
    SET NEIGHBORHOOD;
    IF CLUSTERID ^= 0 THEN DELETE;
RUN;

DATA ALLCLUSTER;
    SET NEIGHBORHOOD;
    IF CLUSTERID = 0 THEN DELETE;
RUN;

** *****************************************************************************;
** Hypothesis 1: The Presence of Commercial Developers will Drive Volunteer Users Away;
** This is primariliy the modularity argument;
** *****************************************************************************;
PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 1: Commercial Developers Drive volunteers to other modules';
    CLASS PROJCLUSTER;
    MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LCOMMERCIALUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr;
RUN;

PROC MIXED DATA=ALLCLUSTER noclprint COVTEST;
    TITLE 'Hypothesis 1a: Commercial Developers Drive volunteers to other modules';
    CLASS PROJCLUSTER;
    MODEL VOLUNTEERUSERS = LVOLUNTEERUSERS LMANUFACTURERUSERS LDISTRIBUTORUSERS/s ddfm=bw;
    RANDOM INTERCEPT /subject=PROJCLUSTER type=un gcorr;
RUN;

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

