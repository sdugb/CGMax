1#include"3dsloader.h"

  2#include<fstream>

  4using namespace std;

  6bool tri_dsLoader(char* f_name,Object* obj)

  7{
   //定义接受容器
   unsigned short    chunk_id;
   unsigned int      chunk_length;
   unsigned char     chunk_char[1];
   unsigned short    chunk_qty;
   unsigned short      i;
   unsigned short    chunk_face_flag_chuck;

   //新建输入流对象
   std::ifstream f_in;
   
   //打开文件
   f_in.open(f_name,ios::binary,0x10) ;  //注意第三个参数的取值，只能是0x10,0x20,0x30,0x40中的一个。其他值会报“invalid sha”错误
   if(f_in.fail()) return false;

   //length表示文件长度
   f_in.seekg(0,ios::end);
   streampos length=f_in.tellg();
   f_in.seekg(0,ios::beg);

   //读取文件
   while(f_in.tellg()<length)
   {
       f_in.read((char*)&chunk_id,sizeof(unsigned short));
       f_in.read((char*)&chunk_length,sizeof(unsigned int));

       switch(chunk_id)
       {
       case 0x4d4d:
           break;

       case 0x3d3d:
           break;

       case 0x4000:
           unsigned char*      p_name;
           p_name=obj->getP_name();
           do
           {
               f_in.read((char*)chunk_char,1);
               *p_name=chunk_char[0];
               ++p_name;
           }while(chunk_char[0]!='\0');
           break;

       case 0x4100:
           break;

       case 0x4110:
           VertexCoord point;
           f_in.read((char*)&chunk_qty,2);
           obj->set_points_num(chunk_qty);

           for(i=0;i<chunk_qty;++i)
           {
               f_in.read((char*)&point.x,4);
               f_in.read((char*)&point.y,4);
               f_in.read((char*)&point.z,4);

               obj->set_points(i,point);
           }
           break;

       case 0x4120:
           Triangle surface;
           f_in.read((char*)&chunk_qty,2);
           obj->set_surfaces_num(chunk_qty);

           for(i=0;i<chunk_qty;++i)
           {
               f_in.read((char*)&surface.a,2);
               f_in.read((char*)&surface.b,2);
               f_in.read((char*)&surface.c,2);

               obj->set_surfaces(i,surface);

               f_in.read((char*)&chunk_face_flag_chuck,2);
           }
           break;

       case 0x4140:
           MappingCoord texture;
           f_in.read((char*)&chunk_qty,2);

           for(i=0;i<chunk_qty;++i)
           {
               f_in.read((char*)&texture.u,4);
               f_in.read((char*)&texture.v,4);


               obj->set_textures(i,texture);
           }

           break;

       default:
           f_in.seekg(chunk_length-6,ios::cur);
       }
   }
   f_in.close();

   return true;

115}