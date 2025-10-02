# Assistant Name Setup Video Tutorial Script

**Duration: 5 minutes**  
**Target: Beginner users**

## Opening (30 seconds)

"Hi, I'm going to show you how to customize your smart home assistant name. Instead of saying 'Alexa, ask Home Assistant,' you'll be able to say 'Alexa, ask Jarvis' or any name you choose. This takes about 10 minutes and works with any Home Assistant setup."

## Step 1: Choose Your Name (45 seconds)

**[Screen: Name examples]**

"First, pick your assistant name. Popular choices include Jarvis, Computer, Smart Home, or House. Your name must be 2-25 characters and can't be Alexa, Amazon, or Echo. Single words work great, or two words like 'Smart Home.'"

**[Screen: Valid/Invalid examples]**

"Valid examples: Jarvis, Computer, Smart Home, House Assistant.  
Invalid: Alexa, 123, @home, or single letters."

## Step 2: Update Lambda Configuration (90 seconds)

**[Screen: AWS Lambda Console]**

"Open your AWS Lambda function. Click Configuration, then Environment Variables."

**[Screen: Environment variables page]**

"Add a new variable called HA_ASSISTANT_NAME. Set the value to your chosen name - I'll use 'Jarvis.'"

**[Screen: Adding variable]**

"Type HA_ASSISTANT_NAME in the key field, Jarvis in the value field, then click Save."

**[Screen: Saved confirmation]**

"Perfect. Lambda now knows your custom name."

## Step 3: Create Custom Skill (2 minutes)

**[Screen: Amazon Developer Console]**

"Smart Home skills can't use custom names, so we need a Custom Skill. Go to developer.amazon.com and sign in."

**[Screen: Create Skill button]**

"Click Create Skill. Name it 'Jarvis Home Assistant' or whatever you chose."

**[Screen: Skill creation form]**

"Select Custom model, Start from scratch, then Create Skill."

**[Screen: Build tab]**

"In the Build tab, click Invocation. Change the invocation name to 'jarvis' - lowercase, no spaces."

**[Screen: JSON Editor]**

"Click JSON Editor and replace the content with this code."

**[Screen: Code being pasted]**

"This code handles basic conversation commands. Change 'jarvis' on line 4 to your name, then Save Model and Build Model."

**[Screen: Endpoint configuration]**

"Go to Endpoint tab, select AWS Lambda ARN, and paste your Lambda function ARN here."

## Step 4: Connect Lambda to Skill (60 seconds)

**[Screen: Lambda Console]**

"Back in Lambda, click Add Trigger, select Alexa Skills Kit."

**[Screen: Skill ID field]**

"Get your Skill ID from the Developer Console - it's in the Build tab under Custom. Paste it here and click Add."

**[Screen: Trigger added]**

"Now Lambda and your skill are connected."

## Step 5: Test Your Setup (45 seconds)

**[Screen: Alexa app or Echo device]**

"Test with phrases like 'Alexa, ask Jarvis to turn on the lights' or 'Alexa, tell Jarvis to lock the doors.'"

**[Screen: Successful response]**

"If it works, you're done! If not, check these common issues:"

**[Screen: Troubleshooting checklist]**

"- Wait 5-10 minutes for skill propagation
- Verify the invocation name matches exactly
- Check Lambda environment variable spelling
- Make sure your skill is enabled in the Alexa app"

## Wrap-up (30 seconds)

**[Screen: Summary]**

"You now have a personalized smart home assistant! Your family can use the same commands with your custom name. For advanced features and troubleshooting, check the documentation links in the description."

**[Screen: End card with links]**

"Thanks for watching! Like and subscribe for more smart home tutorials."

---

## Visual Elements Needed

- **Screenshots**: AWS Lambda console, environment variables page, Amazon Developer Console, skill creation flow
- **Code overlay**: JSON for Custom Skill intent
- **Highlight animations**: Important buttons and fields
- **Text callouts**: Key information and warnings
- **Progress indicator**: Step completion status

## Common Questions Overlay

- **"What if I make a mistake?"** - You can change the name anytime
- **"Will this break anything?"** - No, it's completely additive
- **"Can family members use it?"** - Yes, everyone uses the same name

## Accessibility Notes

- Clear audio narration for each step
- Text overlays for all spoken instructions  
- High contrast highlighting for UI elements
- Closed captions available
