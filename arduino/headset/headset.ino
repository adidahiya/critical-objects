#include <Servo.h>

#define HUMAN_BEHAVIOR_DATA_PREFIX "humanBehaviorState:"
#define GOOD_STATE "good"

//set up gate control servo
Servo gateControl;
const int servoPin = 4;
const int position1 = 5;
const int position2 = 80;

void setup() {
    Serial.begin(9600);
    Serial.write("hello world");
    pinMode(LED_BUILTIN, OUTPUT);

    gateControl.attach(servoPin);
    gateControl.write(position1);

}

bool isFeeding = false;
unsigned long timerAmt = 0;
unsigned long openAmt = 500;


String formerData = "humanBehaviorState:neutral";
String data = "humanBehaviorState:neutral";

void loop() {
    if (Serial.available() > 0) {
        data = Serial.readStringUntil('\n');

        Serial.println(data);
        if (data == "humanBehaviorState:good") {

            //open the gate and 'start' the timer
            gateControl.write(position2);
            timerAmt = millis();
        } else if (data == "humanBehaviorState:bad") {
          //make sure the gate closes immediately if state switches to "bad"
          servo.write(position1);
          timerAmt = 0;
        }

        // if (data.startsWith(HUMAN_BEHAVIOR_DATA_PREFIX)) {
        //     // "humanBehaviorState:good"
        //     // trim off prefix by indexing into char array
        //     char* state = &data[strlen(HUMAN_BEHAVIOR_DATA_PREFIX)];
        //     Serial.println("hello browser");
        // }
    }

     //once the gate has been open long enough, then shut it again
    if(millis() - timerAmt >= openAmt){
      servo.write(position1);
      timerAmt = 0;
    }
}
