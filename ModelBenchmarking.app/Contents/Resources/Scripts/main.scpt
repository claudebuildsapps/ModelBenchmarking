FasdUAS 1.101.10   ��   ��    k             l     ��  ��    &   Model Benchmarking App Launcher     � 	 	 @   M o d e l   B e n c h m a r k i n g   A p p   L a u n c h e r   
  
 l     ��  ��    K E This script launches the Model Benchmarking TUI in a Terminal window     �   �   T h i s   s c r i p t   l a u n c h e s   t h e   M o d e l   B e n c h m a r k i n g   T U I   i n   a   T e r m i n a l   w i n d o w      l     ��������  ��  ��     ��  i         I     ������
�� .aevtoappnull  �   � ****��  ��    Q     i     O    $    k    #       l   ��  ��    4 . Get the absolute path to the script directory     �   \   G e t   t h e   a b s o l u t e   p a t h   t o   t h e   s c r i p t   d i r e c t o r y       r    
 ! " ! m     # # � $ $ j / U s e r s / j o s h k o r n r e i c h / D o c u m e n t s / C o d e / M o d e l B e n c h m a r k i n g " o      ���� 0 projectpath projectPath    % & % l   ��������  ��  ��   &  ' ( ' l   �� ) *��   ) G A Open a new terminal window and navigate to the project directory    * � + + �   O p e n   a   n e w   t e r m i n a l   w i n d o w   a n d   n a v i g a t e   t o   t h e   p r o j e c t   d i r e c t o r y (  , - , I   �� .��
�� .coredoscnull��� ��� ctxt . b     / 0 / b     1 2 1 m     3 3 � 4 4  c d   " 2 o    ���� 0 projectpath projectPath 0 m     5 5 � 6 6 2 "   & &   . / s c r i p t s / r u n . s h   t u i��   -  7 8 7 l   ��������  ��  ��   8  9 : 9 l   �� ; <��   ; + % Set the title of the terminal window    < � = = J   S e t   t h e   t i t l e   o f   t h e   t e r m i n a l   w i n d o w :  > ? > r     @ A @ m     B B � C C $ M o d e l   B e n c h m a r k i n g A n       D E D 1    ��
�� 
titl E 4   �� F
�� 
cwin F m    ����  ?  G H G l   ��������  ��  ��   H  I J I l   �� K L��   K 1 + Activate Terminal to bring it to the front    L � M M V   A c t i v a t e   T e r m i n a l   t o   b r i n g   i t   t o   t h e   f r o n t J  N�� N I   #������
�� .miscactvnull��� ��� null��  ��  ��    m     O O�                                                                                      @ alis    J  Macintosh HD               �Ǳ?BD ����Terminal.app                                                   �����Ǳ?        ����  
 cu             	Utilities   -/:System:Applications:Utilities:Terminal.app/     T e r m i n a l . a p p    M a c i n t o s h   H D  *System/Applications/Utilities/Terminal.app  / ��    R      �� P��
�� .ascrerr ****      � **** P o      ���� 0 errmsg errMsg��    k   , i Q Q  R S R l  , ,�� T U��   T > 8 If there's a permissions error, open System Preferences    U � V V p   I f   t h e r e ' s   a   p e r m i s s i o n s   e r r o r ,   o p e n   S y s t e m   P r e f e r e n c e s S  W X W I  , A�� Y Z
�� .sysodlogaskr        TEXT Y m   , - [ [ � \ \ � M o d e l B e n c h m a r k i n g   n e e d s   p e r m i s s i o n   t o   c o n t r o l   T e r m i n a l .   C l i c k   O K   t o   o p e n   S e c u r i t y   &   P r i v a c y   s e t t i n g s . Z �� ] ^
�� 
btns ] J   . 1 _ _  `�� ` m   . / a a � b b  O K��   ^ �� c d
�� 
dflt c m   2 5 e e � f f  O K d �� g��
�� 
disp g m   8 ;��
�� stic   ��   X  h i h l  B B��������  ��  ��   i  j k j l  B B�� l m��   l * $ Display detailed instructions first    m � n n H   D i s p l a y   d e t a i l e d   i n s t r u c t i o n s   f i r s t k  o p o I  B a�� q r
�� .sysodlogaskr        TEXT q m   B E s s � t th P l e a s e   f o l l o w   t h e s e   s t e p s : 
 
 1 .   I n   t h e   S e c u r i t y   &   P r i v a c y   s e t t i n g s   w i n d o w   t h a t   o p e n s   n e x t 
 2 .   C l i c k   o n   ' P r i v a c y   &   S e c u r i t y '   i n   t h e   s i d e b a r 
 3 .   S c r o l l   d o w n   a n d   c l i c k   o n   ' A u t o m a t i o n ' 
 4 .   F i n d   ' M o d e l B e n c h m a r k i n g '   i n   t h e   l i s t 
 5 .   C h e c k   t h e   b o x   n e x t   t o   ' T e r m i n a l ' 
 6 .   C l o s e   S y s t e m   S e t t i n g s   a n d   t r y   r u n n i n g   t h e   a p p   a g a i n r �� u v
�� 
btns u J   F K w w  x�� x m   F I y y � z z  S h o w   S e t t i n g s��   v �� { |
�� 
dflt { m   L O } } � ~ ~  S h o w   S e t t i n g s | ��  �
�� 
disp  m   R U��
�� stic    � �� ���
�� 
givu � m   X [����,��   p  � � � l  b b��������  ��  ��   �  � � � l  b b�� � ���   � 6 0 Open security settings after user clicks button    � � � � `   O p e n   s e c u r i t y   s e t t i n g s   a f t e r   u s e r   c l i c k s   b u t t o n �  ��� � I  b i�� ���
�� .sysoexecTEXT���     TEXT � m   b e � � � � � | o p e n   ' x - a p p l e . s y s t e m p r e f e r e n c e s : c o m . a p p l e . p r e f e r e n c e . s e c u r i t y '��  ��  ��       �� � ���   � ��
�� .aevtoappnull  �   � **** � �� ���� � ���
�� .aevtoappnull  �   � ****��  ��   � ���� 0 errmsg errMsg �  O #�� 3 5�� B���������� [�� a�� e�������� s y }�������� ����� 0 projectpath projectPath
�� .coredoscnull��� ��� ctxt
�� 
cwin
�� 
titl
�� .miscactvnull��� ��� null�� 0 errmsg errMsg��  
�� 
btns
�� 
dflt
�� 
disp
�� stic   �� 
�� .sysodlogaskr        TEXT
�� stic   
�� 
givu��,�� 
�� .sysoexecTEXT���     TEXT�� j &� �E�O��%�%j O�*�k/�,FO*j 	UW DX 
 ���kv�a a a a  Oa �a kv�a a a a a a  Oa j  ascr  ��ޭ