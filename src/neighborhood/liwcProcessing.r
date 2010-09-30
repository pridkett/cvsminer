# set up the filename to read the data from.  In this case, the onlyKnown.csv contains
# only messages for which we can accurately identify the author of the message
#
# this file is very large and will take a VERY long time to process
filename <- Sys.getenv("HOME") + "/code/cvsminer/data/liwc/neighborhoodOnlyKnown.csv"
# load in the data
known.data <- read.table(filename, sep=",", header=TRUE)

# for each set of words, produce a fractional stat that gives the
# fraction of words in that set that fit into the category
known.data$FracDictWords <- known.data$DictionaryWordCount / known.data$WordCount
known.data$FracPronouns <- known.data$TotalPronouns / known.data$WordCount
known.data$Frac1stPersonSingular <- known.data$X1stPersonSingular / known.data$WordCount
known.data$Frac1stPersonPlural <- known.data$X1stPersonPlural / known.data$WordCount
known.data$FracFirstPersonPronouns <- known.data$TotalFirstPerson / known.data$WordCount
known.data$FracSecondPersonPronouns <- known.data$TotalSecondPerson / known.data$WordCount
known.data$FracThirdPersonPronouns <- known.data$TotalThirdPerson / known.data$WordCount
known.data$FracPronounsFirst <- known.data$TotalFirstPerson / max(known.data$TotalPronouns,1)
known.data$FracPronounsSecond <- known.data$TotalSecondPerson / max(known.data$TotalPronouns,1)
known.data$FracPronounsThird <- known.data$TotalThirdPerson / max(known.data$TotalPronouns,1)
known.data$FracAffectiveOrEmotionalProcesses <- known.data$AffectiveOrEmotionalProcesses / known.data$WordCount
known.data$FracPositiveEmotions <- known.data$PositiveEmotions / known.data$WordCount
known.data$FracNegativeEmotions <- known.data$NegativeEmotions / known.data$WordCount
known.data$FracCognitiveProcesses <- known.data$CognitiveProcesses / known.data$WordCount
known.data$FracSwearWords <- known.data$SwearWords / known.data$WordCount
known.data$FracAchievement <- known.data$Achievement / known.data$WordCount
known.data$FracLeisureActivity <- known.data$LeisureActivity / known.data$WordCount
known.data$FracCommunication <- known.data$Communication / known.data$WordCount
known.data$FracSixLetter <- known.data$SixLetterCount / known.data$WordCount
known.data$FracQuotedLines <- known.data$QuotedLineCount / max(known.data$LineCount,1)
known.data$FracJobOrWork <- known.data$JobOrWork / known.data$WordCount
known.data$FracProgramming <- known.data$Programming / known.data$WordCount
known.data$FracOperatingSystems <- known.data$OperatingSystems / known.data$WordCount
known.data$FracDesktopEnvironments <- known.data$DesktopEnvironments / known.data$WordCount
known.data$FracGnomeApplications <- known.data$GnomeApplications / known.data$WordCount

allTests <- function(input.data) {
	# create volunteer, distributor, manufacturer, and commercial data
	volunteer.data <- subset(input.data, Commercial==0)
	distributor.data <- subset(input.data, Distributor==1)
	manufacturer.data <- subset(input.data, Manufacturer==1)
	commercial.data <- subset(input.data, Commercial==1)

	# print out some of the general information
	print(sprintf("There are %d elements in the volunteer data set", length(volunteer.data$MessageId)))
	print(sprintf("There are %d elements in the distributor data set", length(distributor.data$MessageId)))
	print(sprintf("There are %d elements in the manufacturer data set", length(manufacturer.data$MessageId)))
	print(sprintf("There are %d elements in the commercial data set", length(commercial.data$MessageId)))

	# now do some T-tests

	# examine the length of the messages
	print(t.test(volunteer.data$WordCount, commercial.data$WordCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$WordCount, manufacturer.data$WordCount, paired=FALSE, var.equal=FALSE))

	# examine some of the pronoun stuff
	print(t.test(volunteer.data$Frac1stPersonSingular, commercial.data$Frac1stPersonSingular, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Frac1stPersonSingular, commercial.data$Frac1stPersonSingular, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$Frac1stPersonPlural, commercial.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Frac1stPersonPlural, commercial.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))

	# compare between 1st person singular and plural
	print(t.test(input.data$Frac1stPersonSingular, input.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))
	print(t.test(volunteer.data$Frac1stPersonSingular, volunteer.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))
	print(t.test(commercial.data$Frac1stPersonSingular, commercial.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Frac1stPersonSingular, distributor.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))
	print(t.test(manufacturer.data$Frac1stPersonSingular, manufacturer.data$Frac1stPersonPlural, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracPronouns, commercial.data$FracPronouns, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracPronouns, commercial.data$FracPronouns, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracFirstPersonPronouns, commercial.data$FracFirstPersonPronouns, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracFirstPersonPronouns, manufacturer.data$FracFirstPersonPronouns, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracSecondPersonPronouns, commercial.data$FracSecondPersonPronouns, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracSecondPersonPronouns, manufacturer.data$FracSecondPersonPronouns, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracThirdPersonPronouns, commercial.data$FracThirdPersonPronouns, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracThirdPersonPronouns, manufacturer.data$FracThirdPersonPronouns, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracPronounsFirst, commercial.data$FracPronounsFirst, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracPronounsFirst, manufacturer.data$FracPronounsFirst, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracPronounsSecond, commercial.data$FracPronounsSecond, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracPronounsSecond, manufacturer.data$FracPronounsSecond, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracPronounsThird, commercial.data$FracPronounsThird, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracPronounsThird, manufacturer.data$FracPronounsThird, paired=FALSE, var.equal=FALSE))

	# check some of the cognitive process stuff
	print(t.test(volunteer.data$FracCognitiveProcesses, commercial.data$FracCognitiveProcesses, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracCognitiveProcesses, manufacturer.data$FracCognitiveProcesses, paired=FALSE, var.equal=FALSE))

	# check out some of the emotional stuff
	print(t.test(volunteer.data$FracPositiveEmotions, commercial.data$FracPositiveEmotions, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracPositiveEmotions, manufacturer.data$FracPositiveEmotions, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracNegativeEmotions, commercial.data$FracNegativeEmotions, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracNegativeEmotions, manufacturer.data$FracNegativeEmotions, paired=FALSE, var.equal=FALSE))

	# swear words
	print(t.test(volunteer.data$FracSwearWords, commercial.data$FracSwearWords, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracSwearWords, manufacturer.data$FracSwearWords, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$SwearWords, commercial.data$SwearWords, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$SwearWords, manufacturer.data$SwearWords, paired=FALSE, var.equal=FALSE))

	# achievement
	print(t.test(volunteer.data$Achievement, commercial.data$Achievement, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Achievement, manufacturer.data$Achievement, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracAchievement, commercial.data$FracAchievement, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracAchievement, manufacturer.data$FracAchievement, paired=FALSE, var.equal=FALSE))

	# leisure activity
	print(t.test(volunteer.data$LeisureActivity, commercial.data$LeisureActivity, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$LeisureActivity, manufacturer.data$LeisureActivity, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracLeisureActivity, commercial.data$FracLeisureActivity, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracLeisureActivity, manufacturer.data$FracLeisureActivity, paired=FALSE, var.equal=FALSE))

	# communication
	print(t.test(volunteer.data$Communication, commercial.data$Communication, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Communication, manufacturer.data$Communication, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracCommunication, commercial.data$FracCommunication, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracCommunication, manufacturer.data$FracCommunication, paired=FALSE, var.equal=FALSE))

	# dictionary words
	print(t.test(volunteer.data$DictionaryWordCount, commercial.data$DictionaryWordCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$DictionaryWordCount, manufacturer.data$DictionaryWordCount, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracDictWords, commercial.data$FracDictWords, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracDictWords, manufacturer.data$FracDictWords, paired=FALSE, var.equal=FALSE))

	# six letter
	print(t.test(volunteer.data$SixLetterCount, commercial.data$SixLetterCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$SixLetterCount, manufacturer.data$SixLetterCount, paired=FALSE, var.equal=FALSE))

	# this code, for some reason, crashes R
	# print(t.test(volunteer.data$FracSixLetter, commercial.data$FracSixLetter, paired=FALSE, var.equal=FALSE))
	# print(t.test(distributor.data$FracSixLetter, manufacturer.data$FracSixLetter, paired=FALSE, var.equal=FALSE))

	# email adddresses and http addresses
	print(t.test(volunteer.data$EmailAddressCount, commercial.data$EmailAddressCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$EmailAddressCount, manufacturer.data$EmailAddressCount, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$HttpAddressCount, commercial.data$HttpAddressCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$HttpAddressCount, manufacturer.data$HttpAddressCount, paired=FALSE, var.equal=FALSE))

	# information about the number of lines
	print(t.test(volunteer.data$LineCount, commercial.data$LineCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$LineCount, manufacturer.data$LineCount, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$QuotedLineCount, commercial.data$QuotedLineCount, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$QuotedLineCount, manufacturer.data$QuotedLineCount, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracQuotedLines, commercial.data$FracQuotedLines, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracQuotedLines, manufacturer.data$FracQuotedLines, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracJobOrWork, commercial.data$FracJobOrWork, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracJobOrWork, manufacturer.data$FracJobOrWork, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$JobOrWork, commercial.data$JobOrWork, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$JobOrWork, manufacturer.data$JobOrWork, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracProgramming, commercial.data$FracProgramming, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracProgramming, manufacturer.data$FracProgramming, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$Programming, commercial.data$Programming, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$Programming, manufacturer.data$Programming, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracOperatingSystems, commercial.data$FracOperatingSystems, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracOperatingSystems, manufacturer.data$FracOperatingSystems, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$OperatingSystems, commercial.data$OperatingSystems, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$OperatingSystems, manufacturer.data$OperatingSystems, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracDesktopEnvironments, commercial.data$FracDesktopEnvironments, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracDesktopEnvironments, manufacturer.data$FracDesktopEnvironments, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$DesktopEnvironments, commercial.data$DesktopEnvironments, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$DesktopEnvironments, manufacturer.data$DesktopEnvironments, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$FracGnomeApplications, commercial.data$FracGnomeApplications, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$FracGnomeApplications, manufacturer.data$FracGnomeApplications, paired=FALSE, var.equal=FALSE))

	print(t.test(volunteer.data$GnomeApplications, commercial.data$GnomeApplications, paired=FALSE, var.equal=FALSE))
	print(t.test(distributor.data$GnomeApplications, manufacturer.data$GnomeApplications, paired=FALSE, var.equal=FALSE))

	print("End of T-Tests, checking correlations")
	print("Negative/Positive Emotions Correlations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "NegativeEmotions", "PositiveEmotions"))
	print("Negative/Programming Correlations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "NegativeEmotions", "Programming"))
	print("Negative/Operating System Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "NegativeEmotions", "OperatingSystems"))
	print("Negative/Desktop Environemnts Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "NegativeEmotions", "DesktopEnvironments"))
	print("Negative/GNOME Applciations Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "NegativeEmotions", "GnomeApplications"))

	print("Positive/Programming Correlations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "PositiveEmotions", "Programming"))
	print("Positive/Operating System Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "PositiveEmotions", "OperatingSystems"))
	print("Positive/Desktop Environemnts Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "PositiveEmotions", "DesktopEnvironments"))
	print("Positive/GNOME Applciations Corrrleations")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "PositiveEmotions", "GnomeApplications"))

	print("Second Person/HTTP Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalSecondPerson", "HttpAddressCount"))
	print("Second Person/Email Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalSecondPerson", "EmailAddressCount"))

	print("Third Person/HTTP Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalThirdPerson", "HttpAddressCount"))
	print("Third Person/Email Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalThirdPerson", "EmailAddressCount"))

	print("First Person/HTTP Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalFirstPerson", "HttpAddressCount"))
	print("First Person/Email Addresses")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "TotalFirstPerson", "EmailAddressCount"))
	print("First Person Singular/First Person Plural")
	print(tripleCorr(input.data,volunteer.data, distributor.data, manufacturer.data, "X1stPersonSingular", "X1stPersonPlural"))
}

#
# tripleCorr takes multiple pieces of data and performs pairwise comparisons
# eventually I should figure out the real statistics method for this
#
tripleCorr <- function(alldata, vol, dist, man, field1, field2) {
	c(cor(alldata[field1], alldata[field2]),
	  cor(vol[field1], vol[field2]),
	  cor(dist[field1], dist[field2]),
	  cor(man[field1], man[field2]))
}

allTests(known.data)

#
# at this point we can start looking at information on a user level
#
user.data <- data.frame(do.call("rbind", by(known.data, known.data$PersonId, function(x) colMeans(x[,-1]))))
user.data$MessageCount <- data.frame(table(factor(known.data$PersonId)))

rm(known.data)

print("*******************************************")
print("Now looking at data aggregated across users")
print("*******************************************")

allTests(user.data)
