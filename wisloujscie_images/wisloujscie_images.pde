import codeanticode.syphon.*;
SyphonServer server;


int cols = 5;
int rows = 2;
int tileWidth = 540;
int tileHeight = 960;

int interval = 10000; // miliseconds
int lastTime = 0;

ArrayList<PImage> images = new ArrayList<PImage>();
int[] imagesIndices = new int[10];

void loadImages(String directoryPath) {
  File dir = new File(directoryPath);
  if (dir.isDirectory()) { 
    File[] files = dir.listFiles();
    for (File file : files) {
      String filename = file.getName();
      PImage img = loadImage(file.getAbsolutePath());
      if (img != null) {
        images.add(img);
        println("Loaded: " + filename);
      }
    }
    for(int i=0; i<images.size(); i++) imagesIndices[i] = i;
  } else {
    println("Invalid directory path: " + directoryPath);
  }
}

void shuffle() {
  IntList indicesTmp = new IntList();
  for(int i=0; i<10; i++){
    indicesTmp.append(i);
  }
  
  Boolean done = false;
  while(!done){
    done = true;
    indicesTmp.shuffle();
    for(int i=0; i<10; i++){
      if (indicesTmp.get(i) == imagesIndices[i]){
        done = false;
        break;
      }
    }
  }
  
  for(int i=0; i<10; i++){
    imagesIndices[i] = indicesTmp.get(i);
  }
}

void displayImages(){
  int index = 0;
  for (int y = 0; y < rows; y++) {
    for (int x = 0; x < cols; x++) {
      image(images.get(imagesIndices[index]), x * tileWidth, y * tileHeight, tileWidth, tileHeight);
      index++;
    }
  }
}

void setup(){
  size(2700, 1920);
  loadImages("path...");
  displayImages();
  server = new SyphonServer(this, "wisloujscie_images");
}

void draw(){
  if (millis() - lastTime > interval) {
    shuffle();
    lastTime = millis(); 
    displayImages();
  }
  server.sendScreen();
}
