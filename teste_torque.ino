
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(3000);
  while (!Serial);
}
void loop() {
  String incomingByteString; // para  dados recebidos na porta serial

  // enviar resposta apenas quando receber dados:
  if (Serial.available() > 0) {
  
    // lê o dado recebido:
    incomingByteString = Serial.readString();
    incomingByteString.trim();
    
    Serial.println(incomingByteString);
    
    // responder o que foi recebido:
    //Serial.println("STRT_OF_STRING");
    //for(int i=0;i<sizeof(incomingByte);i++){Serial.write("[");
    //Serial.write(incomingByte[i]);
    //Serial.write("]");
    //Serial.println();}
    //Serial.println("END_OF_STRING");
    
  }
}
