// MultiStepper.pde
// -*- mode: C++ -*-
// Use MultiStepper class to manage multiple steppers and make them all move to 
// the same position at the same time for linear 2d (or 3d) motion.

#include <AccelStepper.h>
#include <MultiStepper.h>
AccelStepper stepperX(1,2,3);
AccelStepper stepperY(1,5,4);
AccelStepper stepperZ(1,8,13);

//// EG X-Y position bed driven by 2 steppers
//// Alas its not possible to build an array of these with different pins for each :-(
//AccelStepper stepper1(AccelStepper::FULL4WIRE, 2, 3, 4, 5);
//AccelStepper stepper2(AccelStepper::FULL4WIRE, 8, 9, 10, 11);

// Up to 10 steppers can be handled as a group by MultiStepper
MultiStepper steppers;
long xTemp = 0;
long yTemp = 0;
long zTemp = 0;
String temp;
String serialString;

void setup() {
  Serial.begin(9600);

  // Configure each stepper
  stepperX.setMaxSpeed(5000);
  stepperY.setMaxSpeed(5000);
  stepperZ.setMaxSpeed(1000);
  //stepperX.setAcceleration(50.0);
  //stepperY.setAcceleration(50.0);
  //stepperZ.setAcceleration(50.0);

  // Then give them to MultiStepper to manage
  steppers.addStepper(stepperX);
  steppers.addStepper(stepperY);
  steppers.addStepper(stepperZ);
  while(1){
      if(Serial.available()){
           serialString = Serial.readStringUntil('#');//$asd;asd;asd#
           move3DStepper(serialString); 
      }  
  } 
}

void move3DStepper(String positions){
    temp = positions;
    long positionsFinal[3];
  
    if(temp.startsWith("$")){
        temp = temp.substring(1, temp.length());
        temp.concat(";");
        
        String position3D[3];
        for(int i = 0; i < 3; i++){
            position3D[i] = temp.substring(0, temp.indexOf(";",0));
            temp.remove(0, temp.indexOf(";",0)+1);  
        }
        
        long xCoordsLeapMotion = position3D[0].toInt();
        long yCoordsLeapMotion = position3D[1].toInt();
        long zCoordsLeapMotion = position3D[2].toInt();      
//        Serial.println(xCoords);
//        Serial.println(yCoords);
//        Serial.println(zCoords);

        //Calculate the real X,Y,Z coordinates to move the steppers
        long xFinalCoords = xCoordsLeapMotion - xTemp;
        long yFinalCoords = yCoordsLeapMotion - yTemp;
        int zFinalCoords = zCoordsLeapMotion - zTemp;

        
        positionsFinal[0] = xFinalCoords;
        positionsFinal[1] = yFinalCoords;
        positionsFinal[2] = zFinalCoords;


        steppers.moveTo(positionsFinal);
        steppers.runSpeedToPosition();

        //Set current position to X, Y, Z
        stepperX.setCurrentPosition(0);
        stepperY.setCurrentPosition(0);
        stepperZ.setCurrentPosition(0);
        stepperX.setMaxSpeed(5000);
        stepperY.setMaxSpeed(5000);
        stepperZ.setMaxSpeed(1000);

        //Re-assign the temp values to current position
        xTemp = xCoordsLeapMotion;
        yTemp = yCoordsLeapMotion;
        zTemp = zCoordsLeapMotion;
    }
}


void loop() {

}
