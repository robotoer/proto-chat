# Print start-of-game Notes + get regen rate
regen <- as.numeric(readline('How many skillpoints regenerate per turn? '))
print('Input 18 as use value to activate all-in.', quote = FALSE)


# Initialize random skillset
skills <- data.frame(c('Subterfuge','Information Gathering','Wetwork','Sabotage','Sexitude','Stoicism'), 1, 1, 1)
names(skills) <- c('Skill name','Min','Max','Current max')
while (any(skills[,2] >= skills[,3])) {
  skills[skills[,2] >= skills[,3],2] <- sample(1:11,length(skills[skills[,2] >= skills[,3],2]), replace = TRUE)
  skills[skills[,2] >= skills[,3],3] <- sample(2:12,length(skills[skills[,2] >= skills[,3],3]), replace = TRUE)
}
skills[,4] <- skills[,3]


# Define regenerate function (currently, skills do not regenerate on a turn in which they are used)
regenerate <- function(set, rate, used) {
  set[set[,3]!=0,4][-used] <- set[set[,3]!=0,4][-used] + rate
  set[set[,4]>set[,3],4] <- set[set[,4]>set[,3],3]
  return(set)
}


# Iterate turns
turn <- 1
for (i in 1:1000) {
  print(c('Turn: ',turn), quote = FALSE)
  print(skills, quote = FALSE)
  input <- as.numeric(unlist(strsplit(readline('What skill do you use? input format: [skill row#],[Use value]: '),',')))
  if ((input[2] > skills[input[1],4] | input[2] < skills[input[1],2]) & input[2]!=18) {
    print('Use value out of selectable range, try again!', quote = FALSE)
  } else if (input[2] == 18) {
    skills[input[1],2:4] <- c(0,0,0)
    skills <- regenerate(skills, regen, input[1])
    turn <- turn+1
  } else { 
    skills[input[1],4] <- skills[input[1],4] - (input[2] - skills[input[1],2] + 1)
    skills <- regenerate(skills, regen, input[1])
    turn <- turn+1
  }
}