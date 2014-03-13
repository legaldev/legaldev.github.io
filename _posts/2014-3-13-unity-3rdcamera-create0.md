---
layout: post
title: Unity第三人称相机构建0
category: unity
tag: dev
---

{{page.title}}
==============

我想在Unity中创建一个第三人称相机，相机的行为参考《魔兽世界》的第三人称相机，具体的需求是：

1. 鼠标左键：控制相机围绕人物旋转，人物不旋转
2. 鼠标右键：控制相机围绕人物旋转，人物的前方向(Unity中的tranform.forward)相应旋转，人物上方向不变
3. 鼠标左键旋转后，再右键旋转，角色前方向马上根据左键的旋转做调整，再根据右键旋转，此时等价于两次都是右键旋转
4. 相机不能穿过任何刚性物体
5. 相机在旋转中碰到地面，停止围绕人物旋转，改为围绕自身旋转

这个需求可以先分成两部分：相机旋转，相机刚性。简单起见，这里先来解决相机旋转的问题，也就是需求的前3点。

相机旋转
-------------
继续细分相机旋转的行为，可以分成左键旋转和右键旋转，下面我们来一步一步地完成这两个旋转。首先我把相机设为人物的子物体(children)，这样人物的一些基本的移动相机都会自动的跟踪。

###左键旋转###
单单看左键旋转，需求很简单：**相机旋转，人物不旋转**，这就相当于一个观察模型的相机，相机可以任意角度观察中心物体。

在Unity中获取鼠标左键状态使用语句：`Input.GetMouseButton(0)`（注：后面涉及到代码的地方，都是使用C#），明显，右键就是`Input.GetMouseButton(1)`。获取鼠标光标的移动位置（可以理解为帧之间光标在X-Y上的偏移量）信息是：`Input.GetAxis("Mouse X"); Input.GetAxis("Mouse Y")`。那么我们可以先来获取鼠标左键按下后光标的移动信息：


```csharp
if (Input.GetMouseButton(0))
{
    float x = Input.GetAxis("Mouse X");
    float y = Input.GetAxis("Mouse Y");
}
```

 
代码很简单，那下面就是关键的地方：如何控制相机来旋转。要理解旋转，这里需要一些关于四元数的知识（网上资料很多，这里就不列举了），四元数重要的一点是它可以很简单地构造旋转，特别是围绕某个向量的旋转，理解四元数后，实现相机围绕人物的旋转就不难了。

另外还有一点要注意的是，四元数旋转轴只是一个向量，以原点为出发点，如果要以世界坐标系中的某点`O`为原点，以该点为出发点的向量`V`为旋转轴，就需要进行坐标系的变换，简单地说，就是把需要旋转的点`P`变换到，以`O`为原点的坐标系中，根据`V`旋转，再变换会世界坐标系。

鼠标左右移动控制相机左右旋转的代码就可以直接给出：

	// 构造一个四元数，以人物的上方向(up)为旋转轴，这是在人物坐标系中的旋转
    Quaternion rotation = Quaternion.AngleAxis(x, transform.parent.up);
    // 这里做的就是坐标系的变换，把相机的世界坐标变换到人物坐标系下的坐标	
    Vector3 offset = transform.position - transform.parent.position;
    // 计算旋转并变换回世界坐标系中
    transform.position = transform.parent.position + (rotation * offset);
    // 调整相机的视角中心
    transform.LookAt(transform.parent);	

`Quaternion`是Unity中表示四元数的类型，加上之前鼠标左键的检测，就可以完成左键控制相机左右旋转。

控制上下旋转比左右旋转麻烦一点，因为此时的旋转轴是会一直变化的(这里假设人物的up一直是Y轴的正方向)。注意的相机也是一直在旋转，并且视点中心一直对准人物，那么相机的右方向(right)就是我们想要围绕着旋转的轴了(把相机right想象成人物的right)，这样理解，那么上下旋转的代码也很简单了：

    Quaternion rotation = Quaternion.AngleAxis(-y, transform.right);
    Vector3 offset = transform.position - transform.parent.position;
    transform.position = transform.parent.position + (rotation * offset);
    transform.LookAt(transform.parent);

###右键旋转###
右键旋转做起来要比左键简单，因为此时人物也会左右旋转，于是我们可以理解为人物带动相机左右旋转，于是我们只需要旋转左右人物：

    transform.parent.Rotate(0, x, 0);

上下旋转跟左键的代码一样。

###先左键，后右键###
上面虽然可以分别左键旋转，右键旋转，但是一旦先用左键旋转，再用右键操作的时候，问题就会出现：人物的前方向和相机的前方向不同了！那么相机和人物的正方向就从此分离，实际操作起来很奇怪。那么我们在用右键旋转的时候就要先把人物调整为跟相机的正方向一致：

    Vector3 oldPosition = transform.position;
    transform.parent.forward = Vector3.Normalize(new Vector3(transform.forward.x, 0, 
    	transform.forward.z));
    transform.position = oldPosition;
    transform.LookAt(transform.parent);

###完整代码###
	if (Input.GetMouseButton(0) ^ Input.GetMouseButton(1))
	{
	    float x = Input.GetAxis("Mouse X") * rotateSpeed;
	    float y = Input.GetAxis("Mouse Y") * rotateSpeed;

	    if (Input.GetMouseButton(1) && x != 0F && y != 0F)
	    {
	        // set character forward to the camera forward
	        Vector3 oldPosition = transform.position;
	        transform.parent.forward = Vector3.Normalize(new Vector3(transform.forward.
	        	x, 0, transform.forward.z));
	        transform.position = oldPosition;
	        transform.LookAt(transform.parent);
	    }

	    if (x != 0F)
	    {
	        if (Input.GetMouseButton(0))    // mouse LB, character not rotate
	        {
	            Quaternion rotation = Quaternion.AngleAxis(x, transform.parent.up);
	            Vector3 offset = transform.position - transform.parent.position;
	            transform.position = transform.parent.position + (rotation * offset);
	            transform.LookAt(transform.parent);
	        }
	        else
	        {
	            transform.parent.Rotate(0, x, 0);
	        }
	    }

	    if (y != 0F)
	    {

	        if ((Vector3.Dot(transform.forward, transform.parent.up) >= -0.9F || y > 0) 
	        &&
	            (Vector3.Dot(transform.forward, transform.parent.up) <= 0.9F || y < 0))
	        {
	            Quaternion rotation = Quaternion.AngleAxis(-y, transform.right);
	            Vector3 offset = transform.position - transform.parent.position;
	            transform.position = transform.parent.position + (rotation * offset);
	            transform.LookAt(transform.parent);

	        }
	    }
	}
