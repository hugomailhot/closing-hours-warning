# closing-hours-warning
Plays a warning message when the UC Davis Shields Library is about to lock its doors.

This script will scrape the Shields Library closing hours, then play a warning
message at regular intervals when the library is about to lock its door.

Past closing time, it will wait until 4am the next morning to scrape the next closing
hours.

### Command-line mp3 player

This script relies on a commmand-line utility that will play an mp3 file.

**For Windows**, make sure that DLC media player can run with this command:  
`dlc -w <filename>`

**For Linux**, use mpg321:  
`mpg321 <filename> -quiet`

**For OSX**, use afplay:  
`afplay <filename>`