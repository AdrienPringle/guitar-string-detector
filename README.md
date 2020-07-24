# guitar-string-detector

I'm not a musician, I just happen to own an electric guitar for testing, so my music/guitar terminology might be horrible. I'm sorry.

#### How this is supposed to work:

1. Record indivudial guitar strings (or anything really, pianos work great)
2. Save the Foruier transform to find the distribution of component frequencies (ranging between 50 and 1500Hz). This is done using saveFFT.py
3. Take in live audio data and compare the Fourier tranform to the saved ones to find the relative weight of the component strings

So far this only works for 6 base notes (E2, A2, etc...) but I have a couple untested ideas on how to expand this for all possible finger combinations


#### Why I think this doesnt work as well as I expected:

The method treats fourier transforms as 1450 dimensional vectors (a single data point for every frequency from 50 to 1500hz) and uses the least squares method to approximate a best fit for the live FT as a sum of the 6 recorded FTs.

This method is very sensitive to out of tune strings, as sharp peaks in an FT may be close but not overlap. If this is the case, the lease squares approximation will assign a weight of close to 0 to the played string, since an out of phase peak would be increasing error. Insturments that have very regular FTs (such as a keyboard) worked very well, but the guitar did not.

However, even when the 6 FTs were recorded immidiately before detecting strings (using the inbuilt tune to string method), the corellation between string volume and detected weight remained weak (althoug it improved by 7 orders of magnitude). This may be due to my low quality strings, but the strength of string frequencies vary over time after they've been plucked. 


#### Ideas I have to fix this

- I could try to find the relative strength of known fundamental and harmonic frequencies in the live FT relative to the average strength. This would probably get complicated as there is a lot of overlap, and a very large number of harmonic frequencies that vary over time
- I could take a moving average of the recorded and live FTs, so that slightly out of tune stings have less of a negative impact. However, I feel like this could harm results for good tuning
- I could find a better approximation method that allows for wiggle room in frequency (but I have no idea what that would be)

- I've already tried detecting peaks in the live FT, but I wasn't able to move forward with this method as I was unable to find a good method that picked out only the peaks I wanted
