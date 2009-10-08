using Microsoft.Xna.Framework; 
using Microsoft.Xna.Framework.Graphics;

namespace CityMania
{
    class DrawSprite
    {
        public Texture2D texture { get; set; }      //  sprite texture, read-only property
        public Vector2 position { get; set; }  //  sprite position on screen
        public Vector2 size { get; set; }      //  sprite size in pixels

        public DrawSprite(Texture2D newTexture, Vector2 newPosition, Vector2 newSize)
        {
            texture = newTexture;
            position = newPosition;
            size = newSize;
        }

        public void Draw(SpriteBatch spriteBatch)
        {
            spriteBatch.Draw(texture, position, Color.White);
        }
    }
}