#region Using Statements

// System
using System;

// XNA
using Microsoft.Xna.Framework;
using Microsoft.Xna.Framework.Content;
using Microsoft.Xna.Framework.Graphics;

#endregion

namespace OpenCity
{
    /// <summary>
    /// A popup message box screen, used to display "are you sure?"
    /// confirmation messages.
    /// </summary>
    class Button : GameScreen
    {
        #region Fields

        // Base
        Vector2 buttonPosition;
        string label;
        int hPadding;
        

        // Button Specific
        Rectangle buttonRectangle = new Rectangle(0, 0, 200, 34);

        // Button Textures
        Texture2D bgLeftTexture;
        Texture2D bgRightTexture;
        Texture2D bgMiddleTexture;

        #endregion

        #region Events

        public event EventHandler<PlayerIndexEventArgs> Accepted;
        public event EventHandler<PlayerIndexEventArgs> Cancelled;

        #endregion

        #region Initialization


        /// <summary>
        /// Constructor automatically sets the disabled function to false.
        /// </summary>
        public Button(string label, Vector2 buttonPosition)
            : this(label, buttonPosition, 6,false)
        { }


        /// <summary>
        /// Constructor lets the caller specify whether to disable the button or not.
        /// </summary>
        public Button(string label, Vector2 buttonPosition, int hPadding, bool disabled)
        {
            IsPopup = true;


            this.hPadding = hPadding;
            this.label = label;
            this.buttonPosition = buttonPosition;
        }


        /// <summary>
        /// Loads graphics content for the buttons. 
        /// This uses the shared ContentManager provided by the Game class.
        /// </summary>
        public override void LoadContent()
        {
            ContentManager content = ScreenManager.Game.Content;

            // Default Button
            bgLeftTexture = content.Load<Texture2D>(@"Images\GUI\Elements\Buttons\Default\Default\bgLeft");
            bgRightTexture = content.Load<Texture2D>(@"Images\GUI\Elements\Buttons\Default\Default\bgRight");
            bgMiddleTexture = content.Load<Texture2D>(@"Images\GUI\Elements\Buttons\Default\Default\bgMiddle");

        }


        #endregion

        #region Handle Input


        /// <summary>
        /// Responds to user input, accepting or cancelling the message box.
        /// </summary>
        public override void HandleInput(InputState input)
        {
            PlayerIndex playerIndex;

            // We pass in our ControllingPlayer, which may either be null (to
            // accept input from any player) or a specific index. If we pass a null
            // controlling player, the InputState helper returns to us which player
            // actually provided the input. We pass that through to our Accepted and
            // Cancelled events, so they can tell which player triggered them.
            if (input.IsMenuSelect(ControllingPlayer, out playerIndex))
            {
                // Raise the accepted event, then exit the message box.
                if (Accepted != null)
                    Accepted(this, new PlayerIndexEventArgs(playerIndex));

                ExitScreen();
            }
            else if (input.IsMenuCancel(ControllingPlayer, out playerIndex))
            {
                // Raise the cancelled event, then exit the message box.
                if (Cancelled != null)
                    Cancelled(this, new PlayerIndexEventArgs(playerIndex));

                ExitScreen();
            }
        }


        #endregion

        #region Draw


        /// <summary>
        /// Draws the message box.
        /// </summary>
        public override void Draw(GameTime gameTime)
        {
            SpriteBatch spriteBatch = ScreenManager.SpriteBatch;
            SpriteFont font = ScreenManager.Font;

            // Create a temporary demo position for the button
            Viewport viewport = ScreenManager.GraphicsDevice.Viewport;
            Vector2 viewportSize = new Vector2((int)viewport.Width, (int)viewport.Height);

            // Padding / Spacing
            const int hSpacing = 4;

            // Main rectangles
            Rectangle labelRectangle = new Rectangle(0,0,
                                                       (int)font.MeasureString(label).X + hPadding * 2,
                                                       (int)font.MeasureString(label).Y);

            Rectangle buttonRectangle = new Rectangle((int)buttonPosition.X - hSpacing,
                                                        (int)buttonPosition.Y,
                                                        (int)labelRectangle.Width + hSpacing * 2,
                                                        (int)labelRectangle.Height);

            // Label positions
            Vector2 labelSize = new Vector2(labelRectangle.X, labelRectangle.Y);
            Vector2 labelPosition = buttonPosition + new Vector2(hPadding + labelSize.X / 2, buttonRectangle.Height / 2 - 4);

            // Button Background Rectangles
            Rectangle bgLeftRectangle = new Rectangle((int)buttonRectangle.X,
                                                        (int)buttonRectangle.Y,
                                                        (int)bgLeftTexture.Width,
                                                        (int)bgLeftTexture.Height);

            Rectangle bgRightRectangle = new Rectangle((int)bgLeftRectangle.X + buttonRectangle.Width - bgRightTexture.Width,
                                                        (int)buttonRectangle.Y,
                                                        (int)bgRightTexture.Width,
                                                        (int)bgRightTexture.Height);

            Rectangle bgMiddleRectangle = new Rectangle((int)buttonRectangle.X + bgLeftRectangle.Width,
                                                        (int)buttonRectangle.Y,
                                                        (int)buttonRectangle.Width - bgLeftRectangle.Width - bgRightRectangle.Width,
                                                        (int)bgMiddleTexture.Height);


            spriteBatch.Begin();

            // Draw the Button
            spriteBatch.Draw(bgLeftTexture, bgLeftRectangle, Color.White);
            spriteBatch.Draw(bgMiddleTexture, bgMiddleRectangle, Color.White);
            spriteBatch.Draw(bgRightTexture, bgRightRectangle, Color.White);
            
            // Draw the label.
            spriteBatch.DrawString(font, label, labelPosition, new Color(64, 74, 104),
                0, labelSize / 2, 1, SpriteEffects.None, 0);

            spriteBatch.End();
        }


        #endregion
    }
}
