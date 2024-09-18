Shape shape;

// Parameters:
int n = 3;
int depth = 30;
float dRotation = 24.0;
float curve = 0.25;
float scale = .9;
float dSize = 0.0;

float[] color1 = {0.0, 0.0, 255.0};
float[] color2 = {255.0, 0.0, 0.0};

float r = 0;
float dr = 0.2;
float r_max = 30.0;
Boolean r_mode = false;

void setup(){
  size(1080, 1920, P2D);
  shape = new Shape(n, color1, color2);
}

// n=4, scale=0.85, dRot=15
// n=3, scale=0.78, dRot=15

void draw(){
  background(0);
  //strokeWeight(2);
  shape.drawShapes(depth, r, curve, scale, dSize);
  saveFrame("path...");
  
  if (frameCount > 1 && r <= 0) exit();
  
  if (r >= r_max && !r_mode) r_mode = true;
  if (!r_mode) r += dr;
  else r -= dr;
  
}

class Shape{
  int vertices;
  float[] c1;
  float[] c2;
  
  
  Shape(int newVertices, float[] newC1, float[] newC2){
     vertices = newVertices;
     c1 = newC1;
     c2 = newC2;
  }
  
  void drawShapes(int depth, float dRotation, float curve, float scale, float dSize){
    println(dRotation);
    float deg = -90.0/vertices;
    float size = 300.0;
    for (int i=0; i<depth; i++){
      drawShape(size, deg, curve);
      deg += dRotation;
      size *= scale;
      size -= dSize;
      size = max(0, size);
    }
  }
  
  void drawShape(float size, float rotation, float curve){
    noFill();
    stroke(255);
    float centerX = width/2;
    float centerY = width/2;
    
    float r = size * curve;
    
    float R = (size - r) * sqrt(2);
    
    float O = 4 * (size-4) + TWO_PI * r;
    float sumO = 0.0;
    float[] prevPoint = new float[2];
    float[] currPoint = new float[2];
    
    noFill();
    stroke(color(color1[0], color1[1], color1[2]));
    
    beginShape();
    for (int i=0; i<vertices; i++){
      float[] arc = getCorner(i*360.0/vertices + rotation, R, r, vertices, size, 50); 
      
      prevPoint[0] = arc[0];
      prevPoint[1] = arc[1];
      for (int j=0; j<=51; j++){
        currPoint[0] = arc[2*j];
        currPoint[1] = arc[2*j+1];
        
        sumO += distance(prevPoint, currPoint);
        
        stroke(getColor(sumO, O));
        vertex(arc[2*j], arc[2*j + 1]);
        
        prevPoint[0] = currPoint[0];
        prevPoint[1] = currPoint[1];
      }
    }
    endShape(CLOSE);
  }
  
  float[] getCorner(float deg, float R, float r, int n, float size, int precision){
    float x = width/2 + R * cos(radians(deg));
    float y = height/2 + R * sin(radians(deg));
    
    float degRange = 180.0/n;
    float dAlpha = 2 * degRange / (precision+1);
    
    float[] arcX = new float[(precision+2)*2];
    
    for (int i=0; i<=precision+1; i++){
      float alpha = deg - degRange + i * dAlpha;
      arcX[2*i] = x + r * cos(radians(alpha));
      arcX[2*i + 1] = y + r * sin(radians(alpha));
    }
    
    
    float [] ret = {1.0};
    return arcX;
  }
  
  color getColor(float sumO, float O){
    float[] newColor = new float[3];
    for (int i=0; i<3; i++){
      newColor[i] = map(abs(sumO - O/2), 0, O/2, color1[i], color2[i]);
    }
    return color(newColor[0], newColor[1], newColor[2]);
  }
}

float distance(float[] p1, float[] p2){
  float sum = 0.0;
  for (int i=0; i<min(p1.length, p2.length); i++){
    sum += (p1[i] - p2[i]) * (p1[i] - p2[i]);
  }
  return sqrt(sum);
}
