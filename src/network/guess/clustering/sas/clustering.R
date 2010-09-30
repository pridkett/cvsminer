# conversion of clustering.sas to R

# needed for time series data
library(nlme)
# needed for multi-level analysis
library(Matrix)

# general fluff functions
if (Sys.getenv("DISPLAY") == "") {
  Sys.putenv(DISPLAY="localhost:10.0")
}

TCOLORS <- list(Aluminum1="#eeeeec", Aluminum2="#d3d7cf", Aluminum3="#babdb6",
                Aluminum4="#888a85", Aluminum5="#555753", Aluminum6="#2e3436",
                Butter1="#fce94f", Butter2="#edd400", Butter3="#c4a000",
                Chameleon1="#8ae234", Chameleon2="#73d216", Chameleon3="#4e9a06",
                Chocolate1="#e9b96e", Chocolate2="#c17d11", Chocolate3="#8f5902",
                Orange1="#fcaf3e", Orange2="#f57900", Orange3="#ce5c00",
                Plum1="#ad7fa8", Plum2="#75507b", Plum3="#5c3566",
                ScarletRed1="#ef2929", ScarletRed2="#cc0000", ScarletRed3="#a40000",
                SkyBlue1="#729fcf", SkyBlue2="#3465a4", SkyBlue3="#204a87")

#' draws a grid on the underlying graph
#'
#' this function is designed to be called in panel.first functions
do.grid <- function(rectcol=TCOLORS$Aluminum2, gridcol=TCOLORS$Aluminum6, dogrid=TRUE) {
  U <- par("usr")
  rect(U[1],U[3],U[2],U[4], col=rectcol)
  if(dogrid) { grid(col=gridcol) }
}














# these names are taken out of timeprocessing.py which builds
# the data file for use in this project
cnames <- c("projectid", "weekid", "clusterid", "commercialcommits",
            "volunteercommits", "activefiles", "commercialusers",
            "volunteerusers", "commercialfiles", "volunteerfiles",
            "crossclustercommits", "commercialcrossclustercommits",
            "volunteercrossclustercommits", "totalperiodcommits",
            "totalperiodfiles", "commercialcrossclusterusers",
            "volunteercrossclusterusers",
            "distributorcommits", "distributorusers",
            "manufacturercommits", "manufacturerusers",
            "newcommercialusers", "newvolunteerusers",
            "newprojectcommercialusers", "newprojectvolunteerusers",
            "newprojectdistributorusers", "newprojectmanufacturerusers",
            "projectvolunteerusers", "projectcommercialusers",
            "projectdistributorusers", "projectmanufacturerusers",
            "continuingVolunteerUsers", "continuingCommercialUsers",
            "continuingDistributorUsers", "continuingManufacturerUsers",

            "redhatu", "novellu", "sunu", "ximianu", "nokiau",
            "openedhandu", "xandrosu", "fluendou", "mandrivau", "conectivau",
            "vasoftwareu", "imendiou", "helixcodeu", "codefactoryu", "suseu",
            "wiprou", "eazelu", "canonicalu",
            "redhatc", "novellc", "sunc", "ximianc", "nokiac",
            "openedhandc", "xandrosc", "fluendoc", "mandrivac", "conectivac",
            "vasoftwarec", "imendioc", "helixcodec", "codefactoryc", "susec",
            "wiproc", "eazelc", "canonicalc",

            "lclusterid", "lcommercialcommits",
            "lvolunteercommits", "lactivefiles", "lcommercialusers",
            "lvolunteerusers", "lcommercialfiles", "lvolunteerfiles",
            "lcrossclustercommits", "lcommercialcrossclustercommits",
            "lvolunteercrossclustercommits", "ltotalperiodcommits",
            "ltotalperiodfiles", "lcommercialcrossclusterusers",
            "lvolunteercrossclusterusers",
            "ldistributorcommits", "ldistributorusers",
            "lmanufacturercommits", "lmanufacturerusers",
            "lnewcommercialusers", "lnewvolunteerusers",
            "lnewprojectcommercialusers", "lnewprojectvolunteerusers",
            "lnewprojectdistributorusers", "lnewprojectmanufacturerusers",
            "lprojectvolunteerusers", "lprojectcommercialusers",
            "lprojectdistributorusers", "lprojectmanufacturerusers",
            "lcontinuingVolunteerUsers", "lcontinuingCommercialUsers",
            "lcontinuingDistributorUsers", "lcontinuingManufacturerUsers",

            "lredhatu", "lnovellu", "lsunu", "lximianu", "lnokiau",
            "lopenedhandu", "lxandrosu", "lfluendou", "lmandrivau", "lconectivau",
            "lvasoftwareu", "limendiou", "lhelixcodeu", "lcodefactoryu", "lsuseu",
            "lwiprou", "leazelu", "lcanonicalu",
            "lredhatc", "lnovellc", "lsunc", "lximianc", "lnokiac",
            "lopenedhandc", "lxandrosc", "lfluendoc", "lmandrivac", "lconectivac",
            "lvasoftwarec", "limendioc", "lhelixcodec", "lcodefactoryc", "lsusec",
            "lwiproc", "leazelc", "lcanonicalc")

indata <- read.table("/home/pwagstro/code/cvsminer/data/clustering/neighborhood.new.csv", sep=",",
                     col.names=cnames)

# create some generated variables
attach(indata)
indata$oldvolunteerusers = volunteerusers - newvolunteerusers
indata$totalcommits = commercialcommits + volunteercommits
indata$users = volunteerusers + commercialusers
indata$ltotalcommits = lcommercialcommits + lvolunteercommits
indata$lusers = lvolunteerusers + lcommercialusers
detach()
attach(indata)
indata$fracvolunteercommits = volunteercommits/max(1,totalcommits)
indata$fraccommercialcommits = commercialcommits/max(1,totalcommits)
indata$fraccrossclusercommits = crossclustercommits/max(1,totalcommits)
indata$fracvolunteerusers = volunteerusers/max(1,users)
indata$fraccommercialusers = commercialusers/max(1,users)
indata$crossclusterusers = commercialcrossclusterusers + volunteercrossclusterusers
indata$fractotalcommits = totalcommits / max(1,totalperiodcommits)
indata$logactivefiles = log(max(activefiles,1))

indata$lfracvolunteercommits = lvolunteercommits/max(1,ltotalcommits)
indata$lfraccommercialcommits = lcommercialcommits/max(1,ltotalcommits)
indata$lfraccrossclusercommits = lcrossclustercommits/max(1,ltotalcommits)
indata$lfracvolunteerusers = lvolunteerusers/max(1,lusers)
indata$lfraccommercialusers = lcommercialusers/max(1,lusers)
indata$lcrossclusterusers = lcommercialcrossclusterusers + lvolunteercrossclusterusers
indata$lfractotalcommits = ltotalcommits / max(1,ltotalperiodcommits)
indata$llogactivefiles = log(max(lactivefiles,1))

indata$projcluster = projectid * 100 + clusterid
detach()

# project 54 is a broken sample because it has no distributor participation
indata <- indata[indata$projectid != 54,]

# create the dummy variables
projectids <- as.integer(levels(as.factor(indata$projectid)))
ctr <- 0
for (projectid in projectids) {
  indata[[sprintf("dummy%d",ctr)]] <- as.integer(indata$projectid == projectid)
  ctr <- ctr + 1
}

nocluster = indata[indata$clusterid==0,]
allcluster = indata[indata$clusterid!=0,]
projclusterids <- as.integer(levels(as.factor(allcluster$projcluster)))

# calculate the appropriate diffs.  We need to do this by project, otherwise
# the normal diff functions won't work properly.  Is there an easier way
# to do this?
newdata <- NA
logcolnames <- c("volunteerusers", "manufacturerusers",
                    "distributorusers", "lvolunteerusers",
                    "lmanufacturerusers", "ldistributorusers",
                    "commercialusers", "lcommercialusers",
                    "totalcommits", "ltotalcommits",
                    "weekid")
for (projectid in projectids) {
  tmpdata <- nocluster[nocluster$projectid==projectid,]
  for (colname in logcolnames) {
    tmpdata[[sprintf("log.%s",colname)]] <-
      log(tmpdata[[colname]]+1)
    tmpdata[[sprintf("diff.log.%s", colname)]] <-
      c(NA, diff(tmpdata[[sprintf("log.%s", colname)]]))
  }
  if (is.null(dim(newdata))) {
    newdata <- tmpdata
  } else {
    newdata <- rbind(newdata, tmpdata)
  }
}
nocluster <- newdata

newdata <- NA
allcluster = indata[indata$clusterid!=0,]
for (projectid in projclusterids) {
  tmpdata <- allcluster[allcluster$projcluster==projectid,]
  for (colname in logcolnames) {
    tmpdata[[sprintf("log.%s",colname)]] <-
      log(tmpdata[[colname]]+1)
    tmpdata[[sprintf("diff.log.%s", colname)]] <-
      c(NA, diff(tmpdata[[sprintf("log.%s", colname)]]))
  }
  if (is.null(dim(newdata))) {
    newdata <- tmpdata
  } else {
    newdata <- rbind(newdata, tmpdata)
  }
}
allcluster <- newdata


# Hypothesis 1
print("Hypothesis 1: Commercial developers drive volunteers to other modules")
fit.lm = lm(volunteerusers ~ lvolunteerusers + lcommercialusers + factor(projectid) - 1, data=allcluster)
summary(fit.lm)
fit.mlm <- lmer(volunteerusers ~ lvolunteerusers + lcommercialusers + (1 | projectid), data=allcluster)
summary(fit.mlm)

print("Hypothesis 1a: Commercial developers drive volunteers to other modules")
fit.lm = lm(volunteerusers ~ lvolunteerusers + lmanufacturerusers + ldistributorusers + factor(projectid) - 1, data=allcluster)
summary(fit.lm)
fit.mlm <- lmer(volunteerusers ~ lvolunteerusers + ldistributorusers + lmanufacturerusers + (1 | projectid), data=allcluster)
summary(fit.mlm)

# Hypothesis 2
print("Hypothesis 2: Commercial developers attract volunteers to projects")
fit.lm <- lm(volunteerusers ~ lvolunteerusers + ldistributorusers + lmanufacturerusers + weekid, data=nocluster)
summary(fit.lm)
print("Hypothesis 2 (cont'd): Why we use projectid as a variable")
fit.lm <- lm(volunteerusers ~ lvolunteerusers + ldistributorusers + lmanufacturerusers + factor(projectid) + weekid- 1, data=nocluster)
summary(fit.lm)
fit.mlm <- lmer(volunteerusers ~ lvolunteerusers + ldistributorusers + lmanufacturerusers + (1 | projectid), data=nocluster)
summary(fit.mlm)
fit.mlm <- lmer(log(volunteerusers+1) ~ log(lvolunteerusers+1) + log(ldistributorusers+1) + log(lmanufacturerusers+1) + (1 | projectid), data=nocluster)
summary(fit.mlm)

# audris would like to see me use the log values of the data
fit.lm = lm(log(volunteerusers+1) ~ log(lvolunteerusers+1) + log(ldistributorusers+1) + log(lmanufacturerusers+1) + factor(projectid) + weekid- 1, data=nocluster)
summary(fit.lm)

# checking out some of the residual issues
pids = as.integer(levels(as.factor(indata$projectid)))

png("acf.fit.png", width=640, height=480)
acf(rstudent(fit.lm), xlim=c(1.5, 30), ylim=c(-0.3, 0.3), main="Autocorrelation of Residuals", panel.first=do.grid(), col=TCOLORS$ScarletRed1, lwd=2)
dev.off()

png("acf.png", width=640, height=480)
acf(diff(nocluster$volunteerusers), xlim=c(1.5, 30), ylim=c(-0.3, 0.3), main="Autocorrelation of diff(VolunteerUsers)", panel.first=do.grid(), col=TCOLORS$ScarletRed1, lwd=2)
dev.off()

png("pacf.png", width=640, height=480)
pacf(diff(nocluster$volunteerusers), xlim=c(1.5, 30), ylim=c(-0.3, 0.3), main="Autocorrelation of diff(VolunteerUsers)", panel.first=do.grid(), col=TCOLORS$ScarletRed1, lwd=2)
dev.off()

png("acf.all.png", width=1600, height=800)




par(mfrow=c(3,5))
par(mar=c(2.1, 2.1, 4.1, 1.1))
for (pid in pids) {
  acf(diff(nocluster[nocluster$projectid==pid,]$volunteerusers), xlim=c(1.5, 30), ylim=c(-0.3, 0.3), main=sprintf("pid=%d", pid), panel.first=do.grid(dogrid=FALSE), col=TCOLORS$ScarletRed1, lwd=2)
}
acf(diff(nocluster$volunteerusers), xlim=c(1.5, 30), ylim=c(-0.3, 0.3), main="All Samples", panel.first=do.grid(dogrid=FALSE), col=TCOLORS$ScarletRed1, lwd=2)
acf(nocluster$volunteerusers, xlim=c(1.5, 30), ylim=c(-0.1, 1.0), main="Undiffed ACF", panel.first=do.grid(dogrid=FALSE), col=TCOLORS$ScarletRed1, lwd=2)

dev.off()

#
# take the diff(log()) values for each of the variables and get the information we need
# save all of this out to summary.log.png
#
png("summary.log.png", width=1600, height=1200)
par(mfrow=c(3,4))
par(mar=c(2.1, 2.1, 4.1, 1.1))
for (column in c("volunteerusers", "distributorusers", "manufacturerusers", "totalperiodcommits")) {
  hist(diff(log(nocluster[[column]]+1)), first=do.grid(), col=TCOLORS$ScarletRed1, lwd=2,
       main=sprintf("Histogram diff(log(%s+1))", column), xlab="") 
}
for (column in c("volunteerusers", "distributorusers", "manufacturerusers", "totalperiodcommits")) {
  acf(diff(log(nocluster[[column]]+1)), first=do.grid(), col=TCOLORS$ScarletRed1, lwd=4,
       main=sprintf("acf diff(log(%s+1))", column), xlab="", xlim=c(1.5, 30), ylim=c(-0.3,0.3)) 
}
for (column in c("volunteerusers", "distributorusers", "manufacturerusers", "totalperiodcommits")) {
  pacf(diff(log(nocluster[[column]]+1)), first=do.grid(), col=TCOLORS$ScarletRed1, lwd=4,
       main=sprintf("pacf diff(log(%s+1))", column), xlab="") 
}
dev.off()


#
# generate figures to support my arguments with audris
#
png("acf.volunteerusers.png", width=640, height=480)
acf(nocluster$volunteerusers, na.action=na.exclude, first=do.grid(),
    main="Autocorrelation of VolunteerUsers", col=TCOLORS$ScarletRed1,
    lwd=4, xlim=c(0, 28), ylim=c(-0.1, 1.0))
dev.off()
pdf("volunteerACF.pdf", width=6, height=4)
acf(nocluster$log.volunteerusers, na.action=na.exclude, first=do.grid(),
    main="Autocorrelation of Volunteer Developers", col=TCOLORS$ScarletRed1,
    lwd=4, xlim=c(0, 28), ylim=c(-0.1, 1.0))
dev.off()


png("acf.diff.log.volunteerusers.png", width=640, height=480)
acf(nocluster$diff.log.volunteerusers, na.action=na.exclude, first=do.grid(),
    main="Autocorrelation of Diff(log(VolunteerUsers))", col=TCOLORS$ScarletRed1,
    lwd=4, xlim=c(1.5,28), ylim=c(-0.25, 0.25))
dev.off()
pdf("diffVolunteerACF.pdf", width=6, height=4)
acf(nocluster$diff.log.volunteerusers, na.action=na.exclude, first=do.grid(),
    main="Autocorrelation of Diff(Volunteer Developers)", col=TCOLORS$ScarletRed1,
    lwd=4, xlim=c(1.5,28), ylim=c(-0.25, 0.25))
dev.off()


pdf("ccfLogPredictors.pdf", width=6, height=8)
par(mfrow=c(4,1))
ccf(nocluster$diff.log.volunteerusers, nocluster$log.volunteerusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), log(VolunteerDevs))")
ccf(nocluster$diff.log.volunteerusers, nocluster$log.commercialusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), log(CommercialDevs))")
ccf(nocluster$diff.log.volunteerusers, nocluster$log.distributorusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), log(CommunityDevs))")
ccf(nocluster$diff.log.volunteerusers, nocluster$log.manufacturerusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), log(ProductDevs))")
dev.off()

png("ccf.diff.log.predictors.png", width=640, height=640)
par(mfrow=c(3,1))
ccf(nocluster$diff.log.volunteerusers, nocluster$log.volunteerusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), log(VolunteerDevs))")
ccf(nocluster$diff.log.volunteerusers, nocluster$diff.log.distributorusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), diff(log(CommunityDevs)))")
ccf(nocluster$diff.log.volunteerusers, nocluster$diff.log.manufacturerusers,
    na.action=na.exclude, first=do.grid(), col=TCOLORS$ScarletRed1,
    lwd=4, main="ccf(diff(log(VolunteerDevs)), diff(log(ProductDevs)))")
dev.off()

#
# generate the regression models that I believe that Audris wants
#

# standard model originally proposed
fit.lm0 <- lm(diff.log.volunteerusers ~ log.lvolunteerusers + log.lcommercialusers + log.ltotalcommits + log.weekid + factor(projectid) - 1, data=nocluster)
pdf(file="qqplotlm0.pdf")
qqnorm(rstudent(fit.lm0), col=TCOLORS$ScarletRed1, first=do.grid(), lwd=2)
abline(0,1, col=TCOLORS$SkyBlue3, lwd=2)
dev.off()

fit.lm1 <- lm(diff.log.volunteerusers ~ log.lvolunteerusers + log.lmanufacturerusers + log.ldistributorusers + log.ltotalcommits + log.weekid + factor(projectid) - 1, data=nocluster)
# plot the QQ-Plot to show the normality of the residuals
pdf(file="qqplotlm1.pdf")
qqnorm(rstudent(fit.lm1), col=TCOLORS$ScarletRed1, first=do.grid(), lwd=2)
abline(0,1, col=TCOLORS$SkyBlue3, lwd=2)
dev.off()


# looking at the current period
fit.lm1.current <- lm(diff.log.volunteerusers ~ log.volunteerusers + log.manufacturerusers + log.distributorusers + factor(projectid) - 1, data=nocluster)

# using the diffs generates a bunch of nonsense
fit.lm2.noproject <- lm(diff.log.volunteerusers ~ diff.log.lvolunteerusers + diff.log.lmanufacturerusers + diff.log.ldistributorusers, data=nocluster)
fit.lm2 <- lm(diff.log.volunteerusers ~ diff.log.lvolunteerusers + diff.log.lmanufacturerusers + diff.log.ldistributorusers + factor(projectid) - 1, data=nocluster)


# hypothesis 4, by cluster
fit.lm4 <- lm(diff.log.volunteerusers ~ log.lvolunteerusers + log.lmanufacturerusers + log.ldistributorusers + log.ltotalcommits + log.weekid + factor(projcluster) - 1, data=allcluster)
pdf(file="qqplotlm4.pdf")
qqnorm(rstudent(fit.lm4), col=TCOLORS$ScarletRed1, first=do.grid(), lwd=2)
abline(0,1, col=TCOLORS$SkyBlue3, lwd=2)
dev.off()

fit.lm4b <- lm(diff.log.volunteerusers ~ log.lvolunteerusers + log.lcommercialusers + log.ltotalcommits + log.weekid + factor(projcluster) - 1, data=allcluster)
pdf(file="qqplotlm4b.pdf")
qqnorm(rstudent(fit.lm4b), col=TCOLORS$ScarletRed1, first=do.grid(), lwd=2)
abline(0,1, col=TCOLORS$SkyBlue3, lwd=2)
dev.off()
