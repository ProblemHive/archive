# meta.R - second look, with metafor, at the per-sample effects deposited by Dang et al. 2025
# (osf.io/j56xz, file ES_Nogo_error.csv; d1 = depletion vs long control, d2 = depletion vs short
# control, d3 = long vs short control; v = sampling variance). Checks c/u44es7 with another program
# and adds what that comment did not compute: other estimators of the between-sample variance,
# a confidence interval for it, a prediction interval, and a test of preregistered vs not.
suppressPackageStartupMessages(library(metafor))
cat(R.version.string, "; metafor", as.character(packageVersion("metafor")), "\n")
dat <- read.csv("ES_Nogo_error.csv", check.names = FALSE)
prereg <- c("Lihua Mao (China)", "Anna Baumert (Germany)", "Lile Jia (Singapore)",
            "Oulmann Zerhouni (France)", "Timur Sevincer (Germany)")
dat$prereg <- as.integer(dat$Author %in% prereg)
dat$online <- as.integer(grepl("^Online", dat$Author))
line <- function(label, r) {
  cat(sprintf("%-44s k=%2d d=%6.3f CI95=[%6.3f,%6.3f] Q=%5.2f tau2=%.4f I2=%4.1f%%\n",
              label, r$k, r$b[1], r$ci.lb, r$ci.ub, r$QE, r$tau2, r$I2))
}

cat("\n== 1. DerSimonian-Laird, as in c/u44es7 and in the authors' script\n")
for (j in 1:3) {
  d <- dat[!is.na(dat[[paste0("d", j)]]), ]
  yi <- d[[paste0("d", j)]]; vi <- d[[paste0("v", j)]]
  line(c("depletion vs long control", "depletion vs short control", "long vs short control")[j],
       rma(yi, vi, method = "DL"))
  if (j == 1) {
    line("  preregistered", rma(yi, vi, method = "DL", subset = d$prereg == 1))
    line("  not preregistered", rma(yi, vi, method = "DL", subset = d$prereg == 0))
    line("  preregistered replications (no first lab)", rma(yi, vi, method = "DL", subset = d$prereg == 1 & !grepl("Mao", d$Author)))
    line("  all except the first laboratory", rma(yi, vi, method = "DL", subset = !grepl("Mao", d$Author)))
    line("  laboratory", rma(yi, vi, method = "DL", subset = d$online == 0))
    line("  online", rma(yi, vi, method = "DL", subset = d$online == 1))
  }
}

yi <- dat$d1; vi <- dat$v1
cat("\n== 2. depletion vs long control (14 samples): does the estimator matter?\n")
for (m in c("DL", "REML", "PM", "SJ", "EB")) line(paste("method", m), rma(yi, vi, method = m))
kh <- rma(yi, vi, method = "REML", test = "knha")
cat(sprintf("REML with Knapp-Hartung: d=%.3f CI95=[%.3f,%.3f] t=%.2f df=%d p=%.2g\n",
            kh$b[1], kh$ci.lb, kh$ci.ub, kh$zval, kh$k - 1, kh$pval))

cat("\n== 3. how much heterogeneity do 14 small samples allow? (Q-profile interval, REML fit)\n")
re <- rma(yi, vi, method = "REML")
ci <- confint(re)
print(round(ci$random, 4))
pr <- predict(re)
cat(sprintf("prediction interval at the REML estimate: [%.3f, %.3f]\n", pr$pi.lb, pr$pi.ub))
tau_hi <- sqrt(ci$random["tau^2", "ci.ub"])
cat(sprintf("with tau at its upper limit %.3f: 95%% of true effects between %.3f and %.3f\n",
            tau_hi, re$b[1] - 1.96 * tau_hi, re$b[1] + 1.96 * tau_hi))

cat("\n== 4. preregistered vs not, as a moderator\n")
mo <- rma(yi, vi, mods = ~ prereg, data = dat, method = "REML")
cat(sprintf("difference (prereg - not) = %.3f, SE %.3f, CI95=[%.3f,%.3f], z=%.2f, p=%.3f\n",
            mo$b[2], mo$se[2], mo$ci.lb[2], mo$ci.ub[2], mo$zval[2], mo$pval[2]))
d2 <- dat[!grepl("Mao", dat$Author), ]
mo2 <- rma(d1, v1, mods = ~ prereg, data = d2, method = "REML")
cat(sprintf("without the first laboratory: difference = %.3f, SE %.3f, z=%.2f, p=%.3f\n",
            mo2$b[2], mo2$se[2], mo2$zval[2], mo2$pval[2]))
on <- rma(yi, vi, mods = ~ online, data = dat, method = "REML")
cat(sprintf("online - laboratory = %.3f, SE %.3f, p=%.3f\n", on$b[2], on$se[2], on$pval[2]))

cat("\n== 5. leave one sample out (REML): range of the pooled d\n")
l1 <- leave1out(re)
cat(sprintf("smallest %.3f (without %s), largest %.3f (without %s); lowest lower CI limit %.3f\n",
            min(l1$estimate), dat$Author[which.min(l1$estimate)],
            max(l1$estimate), dat$Author[which.max(l1$estimate)], min(l1$ci.lb)))

cat("\n== 6. small-sample asymmetry (Egger regression on the standard error; 14 points, low power)\n")
eg <- regtest(re, model = "lm", predictor = "sei")
cat(sprintf("t = %.2f, df = %d, p = %.3f\n", eg$zval, eg$dfs, eg$pval))

cat("\n== 7. pilot (10 minutes, d = 0.09, CI95 -0.22 to 0.39) against the main study\n")
se_p <- (0.39 + 0.22) / 3.92
both <- rma(c(0.09, re$b[1]), c(se_p^2, re$se^2), mods = ~ c(0, 1), method = "FE")
cat(sprintf("difference = %.3f, SE %.3f, z = %.2f, p = %.3f\n", both$b[2], both$se[2], both$zval[2], both$pval[2]))
