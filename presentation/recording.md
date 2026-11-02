# Recording and rehearsal

The prepared narration contains 1,449 whitespace-delimited spoken words. At 145
words per minute plus two seconds per slide, the estimate is about 10:23. At 135
words per minute it is about 11:08. Actual spoken pauses and rehearsal determine
the duration. Aim for 10-11 minutes and measure the final export: the approved
limit is 12:00, including the opening, transitions and closing.

1. Read the report and trace both searches before recording. Edit the spoken
   wording so it is comfortable and remains accurate.
2. Open the editable deck and check the recording view at the intended resolution.
   The table and chart are editable, and each slide has the corresponding script
   and source notes. The PDF is a portable alternative.
3. Record a short microphone sample. Check volume, clipping and background noise.
   Use a quiet room and keep the microphone distance steady.
4. Rehearse once with a stopwatch. Use the storyboard in `script.md` to locate
   sections that need trimming. Preserve the invariants and strongest results.
5. Record the narration yourself. Leave short pauses around the LPS and fallback
   traces so the viewer can follow the indices. Avoid reading every table cell.
6. Edit long pauses and errors, then export at a resolution that keeps byte cells,
   axes and IQR values readable. Watch the entire exported video with headphones.
7. Verify its exact duration is at most 12 minutes. Check the actual uploaded or
   submitted version, audio and access settings before submitting its link/file.

The video requirement remains pending until that real recording is complete.
No recording, upload or submission is represented by the prepared deck.

## Rehearsal questions

- Why are there n-m+1 candidate starts? What happens before computing n-m?
- Trace all 13 naive search comparisons in ABABABAC / ABABAC.
- Why is lps[4]=3 for ABABA? Why does the final C cause several fallbacks?
- What is true of the already matched text immediately before each KMP comparison?
- At i=5, why does matched become 3 while i remains 5? What breaks if matched
  resets to zero at that point?
- Why can KMP be linear even when one text byte is compared more than once?
- Why can naive appear linear when m is held fixed in a text-size sweep?
- What is inside the timed window, and how is preprocessing handled?
- How do timing repetitions differ from the three generated instances?
- What do the error bars show? Why are they not confidence intervals?
- What is the exact formula for the repeated absent family? Check one count.
- Why did almost equal comparison counts fail to predict similar runtime in the
  controlled follow-up? Which hardware explanations remain unmeasured?
- Which observations describe a particular workload rather than a universal winner?
