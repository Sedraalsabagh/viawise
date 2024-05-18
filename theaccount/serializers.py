from rest_framework import serializers
from .models import User,UserProfile,Contact

class SingUpSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields=('first_name','last_name','username','password')

        extra_kword={
            'first_name':{'required':True,'allow_blank':False},
            'last_name':{'required':True,'allow_blank':False},
            'username':{'required':True,'allow_blank':False},
            'password':{'required':True,'allow_blank':False,'min_length':8},


        }


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model =User
        fields=('username','password')

        extra_kword={
             'username':{'required':True,'allow_blank':False},
             'password':{'required':True,'allow_blank':False,'min_length':8}
           
             }
class UserProfileSerializer1(serializers.ModelSerializer):
    
    
    class Meta:
        model =UserProfile
        fields=('user','age','gender','address','marital_status','occupation')

        extra_kword={ 
             
             'age':{'required':False,'allow_blank':True},
              
              'address':{'required':False,'allow_blank':True},
           
             }

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=False , required=False)
    first_name = serializers.CharField(source='user.first_name', read_only=False, required=False)
    last_name = serializers.CharField(source='user.last_name', read_only=False, required=False)

    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name', 'age', 'gender', 'address', 'marital_status', 'occupation')
        extra_kwargs = {
            'age': {'required': False},
            'gender': {'required': False},
            'address': {'required': False},
            'marital_status': {'required': False},
            'occupation': {'required': False},
        }
    def update(self, instance, validated_data):
        
        user_data = validated_data.pop('user', {})
        user_instance = instance.user
        user_instance.username = user_data.get('username', user_instance.username)
        user_instance.first_name = user_data.get('first_name', user_instance.first_name)
        user_instance.last_name = user_data.get('last_name', user_instance.last_name)
        user_instance.save()

        
        return super().update(instance, validated_data)    


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
